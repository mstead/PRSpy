import gtk
import gobject

from prspy.gui.component import GladeComponent
from prspy.github_util import GithubAuthTokenConnector


class OptionsDialog(GladeComponent):

    def __init__(self, parent=None):
        widgets = ["window", "configNotebook", "closeButton"]
        GladeComponent.__init__(self, "options.glade", initial_widget_names=widgets)

        self.window.set_transient_for(parent.window)
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.closeButton.connect("clicked", self._on_close_clicked)

        self.tabs = []

    def add_tab(self, tab_name, options_tab):
        self.tabs.append(options_tab)
        self.configNotebook.append_page(options_tab.get_top_level(), gtk.Label(tab_name))

    def _on_close_clicked(self, button):
        self.window.destroy()


class OptionsDialogTab(GladeComponent):
    def __init__(self, glade_file, widget_names):
        GladeComponent.__init__(self, glade_file, initial_widget_names = widget_names)

    def get_top_level(self):
        raise NotImplementedError("Must implement get_top_level")


class RepositoryOptionsTab(OptionsDialogTab, gobject.GObject):
    __gsignals__ = {
        'on-add-org': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'on-add-repo': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'on-remove-repo': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
    }

    def __init__(self):
        widgets = ["window", "main_content", "propertyField", "addButton",
                   "propertyList", "removeButton", "orgRadioButton"]
        OptionsDialogTab.__init__(self, "repositories_tab.glade", widgets)
        gobject.GObject.__init__(self)

        self.model = gtk.ListStore(str)
        self.propertyList.set_model(self.model)

        column = gtk.TreeViewColumn("Repository")
        self.propertyList.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, "text", 0)

        self.addButton.connect("clicked", self._add)
        self.removeButton.connect("clicked", self._remove)

    def _add(self, button):
        propertyValue = self.propertyField.get_text()
        if not propertyValue:
            return

        if self.orgRadioButton.get_active():
            # Delegate to the controller to fetch the repo names,
            # and update the view.
            self.emit("on-add-org", propertyValue)
        else:
            self.emit("on-add-repo", propertyValue)

        self.propertyField.set_text("")

    def _remove(self, button):
        selection = self.propertyList.get_selection()
        model, iter_to_remove = selection.get_selected()
        if not iter_to_remove:
            return
        self.model.remove(iter_to_remove)
        self.emit("on-remove-repo")

    def set_values(self, values):
        self.model.clear()
        for value in values:
            if value:
                self.model.append([value])

    def get_values(self):
        items = []
        list_iter = self.model.get_iter_first()
        while list_iter != None:
            items.append(self.model.get_value(list_iter, 0))
            list_iter = self.model.iter_next(list_iter)
        return items

    def get_top_level(self):
        return self.main_content


class AuthOptionsTab(OptionsDialogTab, gobject.GObject):
    __gsignals__ = {
        'on-create-auth-token': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
        'on-delete-auth-token': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
        'on-refresh-auth-token': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
    }

    def __init__(self):
        widgets = ["main_content", "usernameField", "passwordField",
                   "messageLabel", "deleteButton", "registerButton",
                   "refreshButton"]
        OptionsDialogTab.__init__(self, "auth_tab.glade", widgets)
        gobject.GObject.__init__(self)

        self.registerButton.connect("clicked", self._on_button_click)
        self.deleteButton.connect("clicked", self._on_button_click)
        self.refreshButton.connect("clicked", self._on_button_click)

    def update(self, auth_token):
        if auth_token:
            self.messageLabel.set_text("PRSpy is already registered.")
            self.deleteButton.show()
            self.refreshButton.show()
            self.registerButton.hide()
        else:
            self.messageLabel.set_text("PRSpy requires an OAuth token to authenticate with github.\n"
                                       "Please enter your github username and password to create one.")
            self.deleteButton.hide()
            self.refreshButton.hide()
            self.registerButton.show()

    def _on_button_click(self, button):
        if not self.usernameField.get_text() or not self.passwordField.get_text():
            return

        if button == self.registerButton:
            self.emit("on-create-auth-token")
        elif button == self.refreshButton:
            self.emit("on-refresh-auth-token")
        else:
            self.emit("on-delete-auth-token")

        # clear the input fields
        self.usernameField.set_text("")
        self.passwordField.set_text("")

    def get_top_level(self):
        return self.main_content


class OptionsDialogController(object):
    def __init__(self, gh_connect, config, parent=None):
        self.gh_connect = gh_connect
        self.config = config
        self.view = OptionsDialog(parent)

        # Repository Configuration Tab
        self.repos_tab = RepositoryOptionsTab()
        self.repos_tab.connect("on-add-org", self._on_add_org)
        self.repos_tab.connect("on-add-repo", self._on_add_repo)
        self.repos_tab.connect("on-remove-repo", self._on_remove_repo)
        self.view.add_tab("Repositories", self.repos_tab)

        # Auth Configuration Tab
        self.auth_tab = AuthOptionsTab()
        self.auth_tab.connect("on-delete-auth-token", self._on_delete_auth_token)
        self.auth_tab.connect("on-create-auth-token", self._on_create_auth_token)
        self.auth_tab.connect("on-refresh-auth-token", self._on_refresh_auth_token)
        self.view.add_tab("Authorization", self.auth_tab)

    def show_view(self):
        repos = self.config.github_repos;
        if not repos:
            repos = []
        else:
            repos = repos.split(",")

        self.repos_tab.set_values(repos)
        self.auth_tab.update(self.config.github_auth_token)
        self.view.show()

    def _on_add_org(self, tab, org_name):
        self._update_repos_list(self.gh_connect.get_repos_for_org(org_name))

    def _on_add_repo(self, tab, repo_name):
        self._update_repos_list([repo_name])

    def _on_remove_repo(self, view):
        # The repo has already been removed from the list.
        # We only need to update with an empty list
        self._update_repos_list()

    def _update_repos_list(self, new_repos=[]):
        all_repos = set(self.repos_tab.get_values())
        all_repos.update(new_repos)
        self.config.set_property("github", "repos", ",".join(all_repos))
        self.config.save()
        self.repos_tab.set_values(sorted(all_repos))

    def _on_create_auth_token(self, tab):
        con = GithubAuthTokenConnector(self.auth_tab.usernameField.get_text(), self.auth_tab.passwordField.get_text())
        existing_token = con.get_token()
        if existing_token:
            # Use the existing token if it is found.
            token = existing_token
        else:
            token = con.create_token()
        self.config.set_property("github", "auth_token", token)
        self.config.save()
        self.auth_tab.update(self.config.github_auth_token)

    def _on_delete_auth_token(self, tab):
        con = GithubAuthTokenConnector(self.auth_tab.usernameField.get_text(), self.auth_tab.passwordField.get_text())
        if con.delete_token():
            self.config.set_property("github", "auth_token", "")
            self.config.save()
        self.auth_tab.update(self.config.github_auth_token)

    def _on_refresh_auth_token(self, tab):
        self._on_create_auth_token(tab)

#
# Copyright (c) 2012 Michael Stead
#
# This file is part of PRSpy.
#
# PRSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PRSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PRSpy.  If not, see <http://www.gnu.org/licenses/>.
#
import pygtk

'''
Contains the views that are presented in this application.
'''
import gtk
import gobject

from prspy.gui.component import GladeComponent
from prspy import utils


class MainView(GladeComponent, gobject.GObject):

    __gsignals__ = {
        'selection-changed': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE,
                             (gobject.TYPE_INT,)),
        'on-double-click': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE,
                             (gobject.TYPE_INT,)),
        'on-quit-clicked': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
        'on-refresh-clicked': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
        'on-options-clicked': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
    }

    def __init__(self, main_view_model):
        widgets = ["window", "event_tree_view", "comments_container", "body",
                   "quit_button", "refresh_button", "preferences_button"]
        GladeComponent.__init__(self, "ghui_main.glade", initial_widget_names=widgets)
        gobject.GObject.__init__(self)

        self.window.connect("delete_event", self.window.hide_on_delete)

        self.model = main_view_model
        # Register for changed events from the model so
        # that the view gets updated.
        self.model.connect("changed", self._on_model_change)

        # Configure toolbar button events.
        self.quit_button.connect("clicked", self._on_button_press)
        self.refresh_button.connect("clicked", self._on_button_press)
        self.preferences_button.connect("clicked", self._on_button_press)

        # Configure treeview events.
        self.tree_view_model = gtk.ListStore(str, str, str, str, str, str)
        self.event_tree_view.set_model(self.tree_view_model)
        self.event_tree_view.get_selection().connect("changed",
                                                     self._on_selection_change)
        self.event_tree_view.connect("row-activated", self._on_row_double_click)

        self._add_column("No.", 0, visible=False)
        self._add_column("Title", 1)
        self._add_column("Repo", 2)
        self._add_column("Owner", 3)
        self._add_column("State", 4)
        self._add_column("Assignee", 5)

        self._clear_details()

    def _on_model_change(self, model, action):
        self.tree_view_model.clear()
        for pull_request in self.model.pull_requests.values():
            assignee = ""
            if pull_request.assignee:
                assignee = pull_request.assignee.login
            self.tree_view_model.append([pull_request.number,
                                         pull_request.title,
                                         pull_request.head.repo.name,
                                         pull_request.user.login,
                                         pull_request.state,
                                         assignee])

    def _add_column(self, title, idx, visible=True):
        column = gtk.TreeViewColumn(title)
        self.event_tree_view.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, "text", idx)
        column.set_visible(visible)

    def _build_comments_container(self, pull_request):
        # Clean out the details container
        self.comments_container.foreach(self._remove_comment)

        for comment in pull_request.get_comments():
            row = self._build_comment(comment.user.login, utils.wrap_text(comment.body, 100))
            self.comments_container.pack_start(row, expand=False, fill=False)
            self.comments_container.set_spacing(10)
        self.comments_container.show_all()

    def _clear_details(self):
        self.body.set_text("")
        self.comments_container.foreach(self._remove_comment)

    def _build_comment(self, name, value):
        label = gtk.Label(name)
        label.set_alignment(xalign=0.0, yalign=0.0)
        label.set_size_request(120, -1)
        value_label = gtk.Label(value)
        value_label.set_alignment(xalign=0.0, yalign=0.0)

        property_row = gtk.HBox()
        property_row.pack_start(label, expand=False, fill=False)
        property_row.pack_start(value_label, expand=True, fill=True)
        return property_row

    def update_details(self, pull_request):
        self._clear_details()
        if pull_request:
            self.body.set_text(utils.wrap_text(pull_request.body, 120))
            self._build_comments_container(pull_request)

    def _remove_comment(self, comment_container):
        self.comments_container.remove(comment_container)

    def _on_selection_change(self, tree_selection):
        model, tree_iter = tree_selection.get_selected()
        if not tree_iter:
            self.emit("selection-changed", -1)
            return

        selection = model.get(tree_iter, 0)
        self.emit("selection-changed", int(selection[0]))

    def _on_row_double_click(self, treeview, path, column):
        tree_iter = treeview.get_model().get_iter(path)
        selection = treeview.get_model().get(tree_iter, 0)
        self.emit("on-double-click", int(selection[0]))

    def _on_button_press(self, button):
        if button == self.quit_button:
            self.emit("on-quit-clicked")
        elif button == self.refresh_button:
            self.emit("on-refresh-clicked")
        elif button == self.preferences_button:
            self.emit("on-options-clicked")

    def on_config_update(self, config):
        self.refresh_button.set_sensitive(len(config.github_auth_token) != 0)


class OptionsDialog(GladeComponent):

    def __init__(self):
        widgets = ["window", "configNotebook", "closeButton"]
        GladeComponent.__init__(self, "options.glade", initial_widget_names=widgets)

        self.tabs = []

        self.closeButton.connect("clicked", self._on_close_clicked)

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
        widgets = ["main_content", "propertyField", "addButton",
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
        'on-create-update-auth-token': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'on-delete-auth-token': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE, ()),
    }

    CREATE_ACTION = "CREATE"
    UPDATE_ACTION = "UPDATE"

    def __init__(self):
        widgets = ["main_content", "usernameField", "passwordField",
                   "messageLabel", "deleteButton", "createUpdateButton"]
        OptionsDialogTab.__init__(self, "auth_tab.glade", widgets)
        gobject.GObject.__init__(self)

        self.createUpdateButton.connect("clicked", self._on_button_click)
        self.deleteButton.connect("clicked", self._on_button_click)

        self.current_action = self.CREATE_ACTION

    def update(self, auth_token):
        if auth_token:
            self.current_action = self.UPDATE_ACTION
            self.messageLabel.set_text("PRSpy is already registered.")
            self.deleteButton.show()
            self.createUpdateButton.set_label("Update")
        else:
            self.current_action = self.CREATE_ACTION
            self.messageLabel.set_text("PRSpy requires an OAuth token to authenticate with github.\n"
                                       "Please enter your github username and password to create one.")
            self.deleteButton.hide()
            self.createUpdateButton.set_label("Create")

    def _on_button_click(self, button):
        if not self.usernameField.get_text() or not self.passwordField.get_text():
            return

        if button == self.createUpdateButton:
            self.emit("on-create-update-auth-token", self.current_action)
        else:
            self.emit("on-delete-auth-token")

        # clear the input fields
        self.usernameField.set_text("")
        self.passwordField.set_text("")

    def get_top_level(self):
        return self.main_content

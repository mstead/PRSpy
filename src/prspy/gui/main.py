import sys
import gtk
import gobject
import webbrowser

from github.CommitComment import CommitComment

from prspy.gui.component import GladeComponent
from prspy import utils
from prspy.github_util import GithubConnect
from prspy.gui.options import OptionsDialogController
import pango
from images import LOADING_IMAGE
from threading import Thread

MAIN_VIEW_MODEL_CLEARED = "cleared"
MAIN_VIEW_MODEL_PULL_REQUEST_ADDED = "pull-request-added"
MAIN_VIEW_MODEL_SET_LIST = "pulls-set-from-list"

class MainViewModel(gobject.GObject):
    """
    Represents the state of the MainView.
    """

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self, gh_connect, config):
        gobject.GObject.__init__(self)
        self.pull_requests = {}
        self.config = config
        self.gh = gh_connect

    def clear(self):
        self.pull_requests.clear()
#        self.treeViewModel.clear()
        self.emit("changed", MAIN_VIEW_MODEL_CLEARED)

    def add(self, pull_request):
        self.pull_requests[pull_request.number] = pull_request
        self.emit("changed", MAIN_VIEW_MODEL_PULL_REQUEST_ADDED)

    def refresh(self):
        repos = []
        if self.config.github_repos:
            repos = self.config.github_repos.split(",")

        pulls = self.gh.get_pull_requests([], repos)

        # Clear and update the pull requests
        self.pull_requests.clear()
        for pull in pulls:
            self.pull_requests[pull.number] = pull
        self.emit("changed", MAIN_VIEW_MODEL_SET_LIST)


class MainView(GladeComponent):

    def __init__(self):
        widgets = ["window", "event_tree_view", "comments_container", "body",
                   "quit_button", "refresh_button", "preferences_button",
                   "comments_tab_list_view", "loading_image", "comments_tab_label"]
        GladeComponent.__init__(self, "ghui_main.glade", initial_widget_names=widgets)

        self.selected_pull = None

        # Configure pull request treeview.
        self.event_tree_view.set_property("enable-grid-lines", True)
        self.tree_view_model = gtk.ListStore(str, str, str, str, str, str, str)
        self.event_tree_view.set_model(self.tree_view_model)
        self.event_tree_view.set_rules_hint(True)

        self._add_column(self.event_tree_view, "No.", 0, visible=False)
        self._add_column(self.event_tree_view, "Title", 1, expand=True)
        self._add_column(self.event_tree_view, "Repo", 2)
        self._add_column(self.event_tree_view, "Owner", 3)
        self._add_column(self.event_tree_view, "State", 4)
        self._add_column(self.event_tree_view, "Assignee", 5)
        self._add_column(self.event_tree_view, "Created", 6)

        self._set_treeview_rows_actionable(self.event_tree_view)

        # configure comments list view
        self.comment_list_view_model = gtk.ListStore(str, str, str, str)
        self.comments_tab_list_view.set_model(self.comment_list_view_model)
        self._add_column(self.comments_tab_list_view, "Author", 0)
        self._add_column(self.comments_tab_list_view, "Comment", 1, markup=True,
                         expand=True)
        self._add_column(self.comments_tab_list_view, "Date", 2)
        self._add_column(self.comments_tab_list_view, "Url", 3, visible=False)
        self.comments_tab_list_view.get_selection().set_mode(gtk.SELECTION_NONE)
        self.comments_tab_list_view.set_rules_hint(True)

        self._set_treeview_rows_actionable(self.comments_tab_list_view)

        # Loading icon init
        self.loading_image.set_from_animation(LOADING_IMAGE)
        self.show_loading(False)

        self._clear_details()

    def _set_treeview_rows_actionable(self, treeview):
        treeview.connect("motion-notify-event", self._on_mouse_on_row)
        treeview.connect("enter-notify-event", self._on_enter_leave_treeview)
        treeview.connect("leave-notify-event", self._on_enter_leave_treeview)

    def _on_enter_leave_treeview(self, widget, event):
        """
        Reset to default cursor.

        Used when mouse enters/leaves a treeview to ensure
        that cursor is reset correctly when mouse is not
        over a row.
        """
        widget.window.set_cursor(None)

    def _on_mouse_on_row(self, widget, event):
        """
        If the mouse is moved over a treeview row, change the
        cursor so that the user is aware that an action will
        be fired if the row is double clicked.
        """
        x, y = widget.get_pointer()
        row_tuple = widget.get_dest_row_at_pos(x, y)
        if not row_tuple:
            widget.window.set_cursor(None)
            return

        cursor = gtk.gdk.Cursor(gtk.gdk.IRON_CROSS)
        widget.window.set_cursor(cursor)

    def _on_list_view_leave(self, widget, event):
        print "Leaving list view\n"

    def show_loading(self, show):
        if show:
            self.loading_image.show()
        else:
            self.loading_image.hide()

    def update(self, pull_requests):
        self.tree_view_model.clear()
        pull_requests.sort(key=lambda pull: pull.head.repo.name.lower, reverse=True)
        for pull_request in pull_requests:
            assignee = ""
            if pull_request.assignee:
                assignee = pull_request.assignee.login
            self.tree_view_model.append([pull_request.number,
                                         pull_request.title,
                                         pull_request.head.repo.name,
                                         pull_request.user.login,
                                         pull_request.state,
                                         assignee,
                                         pull_request.created_at])

    def _add_column(self, treeview, title, idx, visible=True, markup=False,
                    expand=False):
        column = gtk.TreeViewColumn(title)
        treeview.append_column(column)
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = 700
        cell.set_alignment(0.0, 0.0)
        column.pack_start(cell, False)
        if markup:
            column.set_attributes(cell, markup=idx)
        column.add_attribute(cell, "text", idx)
        column.set_visible(visible)
        column.set_expand(expand)



    def _build_comment_text(self, comment):
        if isinstance(comment, CommitComment):
            top_line = None
            if comment.path and comment.line:
                top_line = "%s:%s" % (comment.path, comment.line)
            elif comment.path:
                top_line = comment.path
            elif comment.line:
                top_line = comment.line

            if top_line:
                return '<span size="small" weight="bold">%s</span> <span size="small" weight="bold">%s</span>\n%s' % (
                    comment.commit_id, top_line, comment.body
                )
        return comment.body

    def _clear_details(self):
        self.body.set_text("")
        self.comment_list_view_model.clear()
        #self.comments_container.foreach(self._remove_comment)

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
            AsyncMainWindowUpdate(self, pull_request).start()


    def _remove_comment(self, comment_container):
        self.comments_container.remove(comment_container)

    def on_config_update(self, config):
        self.refresh_button.set_sensitive(len(config.github_auth_token) != 0)

    def show_error_dialog(self, err):
        dialog = gtk.MessageDialog(self.window,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, "An error has occurred.\n\n%s" % err.message)
        dialog.run()
        dialog.destroy()


class MainViewController(object):

    def __init__(self, config):
        self.config = config
        self.config.connect("on-change", self._on_config_change)

        self.gh = GithubConnect(self.config.github_auth_token, self.config.prspy_debug == "True")

        self.model = MainViewModel(self.gh, self.config)
        self.view = MainView()

        # register for exit
        self.view.window.connect("destroy", self._on_close)

        # Register for changed events from the model so
        # that the view can be told to update.
        self.model.connect("changed", self._on_model_change)

        self._first_show = True


        # Configure view's toolbar button events.
        self.view.quit_button.connect("clicked", self._on_quit_clicked)
        self.view.refresh_button.connect("clicked", self._on_refresh_clicked)
        self.view.preferences_button.connect("clicked", self._show_options_dialog)

        # When the selection changes in the view, update
        # the view's detail pain with the correct model data.
        self.view.event_tree_view.get_selection().connect("changed",
                                                     self._on_selection_change)

        # When a row is double clicked, open the pull request in the
        # default browser.
        self.view.event_tree_view.connect("row-activated", self._on_pull_request_row_double_click)

        # When a comment row is doubleclicked, open it in the browser.
        self.view.comments_tab_list_view.connect("row-activated", self._on_comment_row_double_click)

    def show_main_view(self):
        # If it is the first time that the main view
        # was shown, load the data.
        self.view.show()
        self.view.on_config_update(self.config)
        if self.config.github_auth_token and self._first_show:
            self.refresh_model()

        if self._first_show:
            self._first_show = False

    def refresh_model(self):
        self.model.refresh()

    def _on_config_change(self, config):
        #update our github connection as the token may have changed
        # from the options dialog.
        self.gh.reconfigure(self.config.github_auth_token)
        self.view.on_config_update(self.config)

    def _on_model_change(self, model, cause):
        self.view.update(model.pull_requests.values())

    def _on_selection_change(self, tree_selection):
        self.view.comments_tab_label.set_text("Comments")
        model, tree_iter = tree_selection.get_selected()
        if not tree_iter:
            self.view.update_details(None)
            return

        selection = model.get(tree_iter, 0)
        pull_request_num = int(selection[0])

        pull = None
        if pull_request_num >= 0:
            pull = self.model.pull_requests[pull_request_num]
        self.view.selected_pull = pull
        self.view.update_details(pull)

    def _on_pull_request_row_double_click(self, treeview, path, column):
        tree_iter = treeview.get_model().get_iter(path)
        selection = treeview.get_model().get(tree_iter, 0)
        pull_request_num = int(selection[0])
        self._open_pull_request_in_browser(pull_request_num)

    def _on_comment_row_double_click(self, treeview, path, column):
        tree_iter = treeview.get_model().get_iter(path)
        selection = treeview.get_model().get(tree_iter, 3)
        url = selection[0]
        self._open_comment_in_browser(url)

    def _open_pull_request_in_browser(self, pull_request_num):
        if not pull_request_num in self.model.pull_requests:
            return

        pull_request = self.model.pull_requests[pull_request_num]
        webbrowser.open(pull_request.html_url, 0, True)

    def _open_comment_in_browser(self, url):
        if not url:
            return
        webbrowser.open(url, 0, True)

    def _on_quit_clicked(self, button):
        self.quit()

    def _on_close(self, window):
        self.quit()

    def quit(self):
        gtk.main_quit()

    def _on_refresh_clicked(self, button):
        self.refresh_model()

    def _show_options_dialog(self, button):
        options_controller = OptionsDialogController(self.gh, self.config, self.view)
        options_controller.show_view()

class AsyncMainWindowUpdate(Thread):
    def __init__(self, main_window, pull_request):
        Thread.__init__(self)
        self.main_window = main_window
        self.pull_request = pull_request

    def run(self):
        try:
            # Show loading icon
            gtk.threads_enter()
            self.main_window.show_loading(True)
            gtk.threads_leave()

            comments = []
            comments.extend(list(self.pull_request.get_comments()))
            comments.extend(list(self.pull_request.get_issue_comments()))

            for commit in list(self.pull_request.get_commits()):
                comments.extend(commit.get_comments())

            comments.sort(key=lambda comment: comment.created_at)

            # Only update if the currently selected pull request is
            # still selected after the comments are pulled from the
            # server.
            if self.main_window.selected_pull != self.pull_request:
                return

            gtk.threads_enter()
            self.main_window.comments_tab_label.set_text("Comments (%s)" % len(comments))
            gtk.threads_leave()

            for comment in comments:
                gtk.threads_enter()
                self.main_window.comment_list_view_model.append([comment.user.login,
                                                     self.main_window._build_comment_text(comment),
                                                     comment.created_at, comment.html_url])
                gtk.threads_leave()

            # Hide loading icon after we are done.
            gtk.threads_enter()
            self.main_window.show_loading(False)
            gtk.threads_leave()
        except Exception, e:
            gtk.threads_enter()
            self.main_window.show_error_dialog(e)
            gtk.threads_leave()


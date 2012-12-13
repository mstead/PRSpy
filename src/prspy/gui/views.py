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
    }

    def __init__(self, main_view_model):
        widgets = ["window", "event_tree_view", "comments_container", "body"]
        GladeComponent.__init__(self, "ghui_main.glade", initial_widget_names=widgets)
        gobject.GObject.__init__(self)

        self.window.connect("delete_event", self.window.hide_on_delete)

        self.model = main_view_model
        # Register for changed events from the model so
        # that the view gets updated.
        self.model.connect("changed", self._on_model_change)

        self.tree_view_model = gtk.ListStore(str, str, str, str, str, str)
        self.event_tree_view.set_model(self.tree_view_model)
        self.event_tree_view.get_selection().connect("changed",
                                                     self._on_selection_change)

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

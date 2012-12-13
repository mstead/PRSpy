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
Contains the models associated with the view of the application.
'''

import gtk
import gobject

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

    def __init__(self):
        gobject.GObject.__init__(self)
        self.pull_requests = {}

    def set_from_list(self, pulls):
        self.pull_requests.clear()
        for pull in pulls:
            self.pull_requests[pull.number] = pull
        self.emit("changed", MAIN_VIEW_MODEL_SET_LIST)

    def clear(self):
        self.pull_requests.clear()
#        self.treeViewModel.clear()
        self.emit("changed", MAIN_VIEW_MODEL_CLEARED)

    def add(self, pull_request):
        self.pull_requests[pull_request.number] = pull_request
        self.emit("changed", MAIN_VIEW_MODEL_PULL_REQUEST_ADDED)
#        assignee = ""
#        if pull_request.assignee:
#            assignee = pull_request.assignee.login
#        self.treeViewModel.append([pull_request.number,
#                               pull_request.title,
#                               pull_request.head.repo.name,
#                               pull_request.user.login,
#                               pull_request.state,
#                               assignee])

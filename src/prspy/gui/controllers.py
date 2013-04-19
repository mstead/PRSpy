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
import sys

'''
Contains the controllers for the various parts of the application.
'''
import webbrowser

from prspy.gui.models import MainViewModel
from prspy.gui.views import MainView
from prspy.github_util import GithubConnect

class MainViewController(object):

    def __init__(self, config):
        self.config = config
        self.gh = GithubConnect(config.github_auth_token)
        self.model = MainViewModel()
        self.view = MainView(self.model)

        self._first_show = True

        # When the selection changes in the view, update
        # the view's detail pain with the correct model data.
        self.view.connect("selection-changed", self._on_selection_change)

        # When a row is double clicked, open the pull request in the
        # default browser.
        self.view.connect("on-double-click", self._open_pull_request_in_browser)

        # listen for the quit button press
        self.view.connect("on-quit-clicked", self._on_quit_clicked)

        # refresh button was clicked in the view
        self.view.connect("on-refresh-clicked", self._on_refresh_clicked)

    def show_main_view(self):
        # If it is the first time that the main view
        # was shown, load the data.
        self.view.show()
        if self._first_show:
            self.refresh_model()
            self._first_show = False

    def refresh_model(self):
        self.model.set_from_list(self.gh.get_pulls_from_repos(
                                    self.config.github_org_id))

    def _on_model_change(self, model, cause):
        self.view.update(model.pull_requests)

    def _on_selection_change(self, view, pull_request_num):
        pull = None
        if pull_request_num >= 0:
            pull = self.model.pull_requests[pull_request_num]
        self.view.update_details(pull)

    def _open_pull_request_in_browser(self, view, pull_request_num):
        if not pull_request_num in self.model.pull_requests:
            return

        pull_request = self.model.pull_requests[pull_request_num]
        webbrowser.open(pull_request.html_url, 0, True)

    def _on_quit_clicked(self, button):
        sys.exit(0)

    def _on_refresh_clicked(self, button):
        self.refresh_model()
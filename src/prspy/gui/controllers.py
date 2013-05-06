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
from prspy.gui.views import MainView, OptionsDialog, RepositoryOptionsTab,\
    AuthOptionsTab
from prspy.github_util import GithubConnect, GithubAuthTokenConnector

class MainViewController(object):

    def __init__(self, config):
        self.config = config
        self.config.connect("on-change", self._on_config_change)

        self.gh = GithubConnect(config.github_auth_token, self.config.prspy_debug == "True")
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

        # Open options dialog when options button is clicked.
        self.view.connect("on-options-clicked", self._show_options_dialog)

    def show_main_view(self):
        # If it is the first time that the main view
        # was shown, load the data.
        self.view.show()
        self.view.on_config_update(self.config)
        if self._first_show:
            self._first_show = False
        if self.config.github_auth_token and self._first_show:
            self.refresh_model()

    def refresh_model(self):

        repos = []
        if self.config.github_repos:
            repos = self.config.github_repos.split(",")


        self.model.set_from_list(self.gh.get_pull_requests([], repos))

    def _on_config_change(self, config):
        #update our github connection as the token may have changed
        # from the options dialog.
        self.gh = GithubConnect(self.config.github_auth_token, self.config.prspy_debug == "True")
        self.view.on_config_update(self.config)

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

    def _show_options_dialog(self, button):
        options_controller = OptionsDialogController(self.gh, self.config)
        options_controller.show_view()


class OptionsDialogController(object):
    def __init__(self, gh_connect, config):
        self.gh_connect = gh_connect
        self.config = config
        self.view = OptionsDialog()

        # Repository Configuration Tab
        self.repos_tab = RepositoryOptionsTab()
        self.repos_tab.connect("on-add-org", self._on_add_org)
        self.repos_tab.connect("on-add-repo", self._on_add_repo)
        self.repos_tab.connect("on-remove-repo", self._on_remove_repo)
        self.view.add_tab("Repositories", self.repos_tab)

        # Auth Configuration Tab
        self.auth_tab = AuthOptionsTab()
        self.auth_tab.connect("on-delete-auth-token", self._on_delete_auth_token)
        self.auth_tab.connect("on-create-update-auth-token", self._on_create_update_auth_token)
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

    def _on_create_update_auth_token(self, tab, action):
        con = GithubAuthTokenConnector(self.auth_tab.usernameField.get_text(), self.auth_tab.passwordField.get_text())
        if action == AuthOptionsTab.UPDATE_ACTION:
            self._on_delete_auth_token(tab)
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



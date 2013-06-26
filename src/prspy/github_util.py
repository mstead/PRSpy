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

from github import Github, enable_console_debug_logging
from prspy.model import PullRequest
from github.GithubException import GithubException

class GithubConnect(object):
    def __init__(self, gh_auth_token, debug=False):
        if debug:
            enable_console_debug_logging()

        self._connection = Github(gh_auth_token)

    def reconfigure(self, gh_auth_token):
        self._connection = self._connection = Github(gh_auth_token)

    def get_pull_requests(self, orgs, repos):
        pulls = []
        for org in orgs:
            pulls.extend(self._get_pull_requests_for_org(org))

        for repo in repos:
            pulls.extend(self._get_pull_requests_for_repo(repo))

        return pulls

    def get_repos_for_org(self, org_name):
        repos = []
        org = self._connection.get_organization(org_name)
        for repo in list(org.get_repos()):
            repos.append(repo.full_name)
        return repos

    def _get_pull_requests_for_org(self, org):
        pulls = []
        try:
            org = self._connection.get_organization(org)
        except GithubException, e:
            print e
            return []

        for repo in list(org.get_repos()):
            pulls.extend(list(repo.get_pulls()))

        return pulls

    def _get_pull_requests_for_repo(self, repo_name):
        try:
            repo = self._connection.get_repo(repo_name)
        except GithubException, e:
            print e
            return []

        return list(repo.get_pulls())


    def get_pull_request(self, repo_name, pull_number, org=None):
        if org:
            source = self._connection.get_organization(org)
        else:
            source = self._connection.get_user()

        repo = source.get_repo(repo_name)
        return PullRequest(repo.get_pull(int(pull_number)));

class GithubAuthTokenConnector(object):

    __DEFAULT_SCOPES = ["public_repo", "repo"]
    __DEFAULT_NOTE = "PRSpy"

    def __init__(self, username, password):
        self.gh = Github(username, password)

    def _get_auth(self):
        user = self.gh.get_user()
        auths = list(user.get_authorizations())
        for auth in auths:
            if auth.note == self.__DEFAULT_NOTE:
                return auth
        return None

    def get_token(self):
        auth = self._get_auth()
        if auth:
            return auth.token
        return None

    def delete_token(self):
        auth = self._get_auth()
        if not auth:
            return False

        try:
            auth.delete()
            return True
        except GithubException:
            return False

    def create_token(self):
        user = self.gh.get_user()
        auths = list(user.get_authorizations())
        for auth in auths:
            if auth.note == self.__DEFAULT_NOTE:
                # Key already exists.
                return auth.token

        auth = user.create_authorization(scopes = self.__DEFAULT_SCOPES, note=self.__DEFAULT_NOTE)
        return auth.token


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

from github import Github
from prspy.model import PullRequest

class GithubConnect(object):
    def __init__(self, gh_auth_token):
        self._connection = Github(gh_auth_token)

    def get_repos_for_org(self, org):
        org = self._connection.get_organization(org)
        return list(org.get_repos())

    def get_pulls_from_repos(self, org_name):
        pulls = []
        repos = self.get_repos_for_org(org_name)
        for repo in repos:
            pulls.extend(list(repo.get_pulls()))
        return pulls

    def get_pull_request(self, repo_name, pull_number, org=None):
        if org:
            source = self._connection.get_organization(org)
        else:
            source = self._connection.get_user()

        repo = source.get_repo(repo_name)
        return PullRequest(repo.get_pull(int(pull_number)));


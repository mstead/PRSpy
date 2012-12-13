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

class PullRequest(object):
    """
    A wrapper class around a Github PullRequest object.

    This class loads lazy loaded objects (i.e Comments) of
    the PyGithub PullRequests. This is so that the required
    data gets loaded up front when displayed in the UI for
    example.
    """
    def __init__(self, ghLazyPullRequest):
        self._gh_pull_request = ghLazyPullRequest
#        self.repo_name = self._gh_pull_request.head.repo.name
#        self.comments = list(self._gh_pull_request.get_comments())
#        self.review_comments = list(self._gh_pull_request.get_review_comments())
#        self.owner = self._gh_pull_request.user.login

    def __getattr__(self, name):
        """
        Only called when this object does not have the specified
        attribute. Delegates to the wrapped object.
        """
        return getattr(self._gh_pull_request, name)


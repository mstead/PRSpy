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
import os
import ConfigParser
import httplib
import simplejson
from getpass import getpass

from prspy.utils import get_input


# General Application
GITHUB_API_URL = "api.github.com"
APP_HOME_DIR = os.path.expanduser("~/.prspy")
APP_LOG_FILE = os.path.join(APP_HOME_DIR, "prspy.log")
CONFIG_FILE = os.path.join(APP_HOME_DIR, "prspy.conf")

if not os.path.exists(APP_HOME_DIR):
    os.mkdir(APP_HOME_DIR)


class NotConfiguredError(Exception):
    pass


class PRSpyConfig(object):

    def __init__(self):
        if not os.path.isfile(CONFIG_FILE):
            raise NotConfiguredError("Config file not found")

        self.parser = ConfigParser.SafeConfigParser()
        if not self.parser.read(CONFIG_FILE):
            raise NotConfiguredError("Unable to read config file.")

        for section in self.parser.sections():
            for option in self.parser.options(section):
                setattr(self, "%s_%s" % (section, option), self.parser.get(section, option))

        self._validate_all()

    def set_property(self, section, option, value):
        self.parser.set(section, option, value)
        setattr(self, "%s_%s" % (section, option), value)

    def save(self):
        self.parser.write(file(CONFIG_FILE, "w"))

    def _validate_all(self):
        self._validate("github", "auth_token")
        self._validate("github", "org_id")
        self._validate("github", "orgs")
        self._validate("github", "repos")

    def _validate(self, section, option):
        attr_name = "%s_%s" % (section, option)
        if not hasattr(self, attr_name):
            raise NotConfiguredError("Missing configuration property: [%s] %s" % (section, option))


class ConfigBuilder(object):

    def build(self):
        auth_token, org_id = self._get_config_values()
        parser = ConfigParser.SafeConfigParser()
        parser.add_section("github")
        parser.set("github", "auth_token", auth_token)
        parser.set("github", "org_id", org_id)
        parser.write(file(CONFIG_FILE, "w"))
        config = PRSpyConfig()
        print "PRSpy was properly configured."
        print "Launching PRSpy..."
        return config

    def _get_config_values(self):
        print "PRSpy requires an Oauth token to communicate to the github API."
        username = get_input("Github Username: ")
        password = getpass("Github Password")
        key_note = get_input("Short Token Description: ")
        auth = "%s:%s" % (username, password)
        auth = auth.encode("base64").rstrip()

        headers = {
            "Authorization": "Basic %s" % auth,
            "Content-Type": "application/json"
        }

        body = '{"scopes":["public_repo", "repo"], "note":"%s"}' % key_note

        conn = httplib.HTTPSConnection("api.github.com")
        conn.request("POST", "/authorizations", body, headers)
        response = conn.getresponse()
        if response.status != 201:
            print "Could not create github API token."
            sys.exit(1)

        auth_json = simplejson.loads(response.read())
        if not 'token' in auth_json:
            print "Unable to create Github API token in response."
            sys.exit(1)

        api_auth_token = auth_json['token']

        org = get_input("Which organization would you like to track? ")
        return (api_auth_token, org)


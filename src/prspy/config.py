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
import gobject


# General Application
GITHUB_API_URL = "api.github.com"
APP_HOME_DIR = os.path.expanduser("~/.prspy")
APP_LOG_FILE = os.path.join(APP_HOME_DIR, "prspy.log")
CONFIG_FILE = os.path.join(APP_HOME_DIR, "prspy.conf")

if not os.path.exists(APP_HOME_DIR):
    os.mkdir(APP_HOME_DIR)


class NotConfiguredError(Exception):
    pass

class ConfigurationError(Exception):
    pass

class PRSpyConfig(gobject.GObject):
    __gsignals__ = {
        'on-change': (gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE,
                              ()),
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.parser = ConfigParser.SafeConfigParser()
        if os.path.exists(CONFIG_FILE) and os.path.isfile(CONFIG_FILE):
            if not self.parser.read(CONFIG_FILE):
                raise NotConfiguredError("Unable to read config file.")
        else:
            # Create a default configuration
            self.parser.add_section("prspy")
            self.parser.set("prspy", "debug", "False")

            self.parser.add_section("github")
            self.parser.set("github", "auth_token", "")
            self.parser.set("github", "repos", "")
            self.parser.write(file(CONFIG_FILE, "w"))

        self._validate_all()

        for section in self.parser.sections():
            for option in self.parser.options(section):
                setattr(self, "%s_%s" % (section, option), self.parser.get(section, option))

    def set_property(self, section, option, value):
        self.parser.set(section, option, value)
        setattr(self, "%s_%s" % (section, option), value)

    def save(self):
        self.parser.write(file(CONFIG_FILE, "w"))
        self.emit("on-change")

    def _validate_all(self):
        self._validate("prspy", "debug")
        self._validate("github", "auth_token")
        self._validate("github", "repos")

    def _validate(self, section, option):
        if not self.parser.has_section(section):
            raise ConfigurationError("Missing configuration section: %s" % section)

        if not self.parser.has_option(section, option):
            raise ConfigurationError("Missing option for % section: %s" % (section, option))


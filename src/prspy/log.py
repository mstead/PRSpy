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

import logging
from prspy import config

class Logger(object):

    def __init__(self, logger_desc, file_path):
        self.logger = logging.getLogger(logger_desc)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(file_path)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

NOTIFY_LOGGER = Logger("PRSPY", config.APP_LOG_FILE).logger
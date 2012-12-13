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

from os import linesep
import textwrap

def wrap_text(s, max_chars):
    # Split the initial strings on linesep.
    # textwrap does not keep them.
    split = s.split(linesep)

    updated = []
    for part in split:
        dedent = textwrap.dedent(part).strip()
        updated.append(textwrap.fill(dedent, max_chars))
    return "\n".join(updated)


def get_yes_no(prompt):
    while 1:
        value = raw_input("%s (Y/N)" % prompt)
        if value and value.upper() == "N":
            return False
        if value and value.upper() == "Y":
            return True
    return False

def get_input(prompt, allow_empty=False):
    user_input = ""
    while not user_input:
        user_input = raw_input(prompt)
        if allow_empty and not user_input:
            break

    return user_input
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

import os
import gtk
import gobject

GLADE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class GladeComponent(object):

    def __init__(self, glade_file, initial_widget_names=['window']):
        self.builder = gtk.Builder()
        self.glade_xml = self.builder.add_from_file(os.path.join(GLADE_DATA_DIR, glade_file))

        if initial_widget_names:
            self._pull_widgets(initial_widget_names)

    def _pull_widgets(self, names):
        for name in names:
            setattr(self, name, self.builder.get_object(name))

    def show(self):
        self.window.present()

class StatusIcon(gtk.StatusIcon, gobject.GObject):

    __gsignals__ = {
        'force_clicked' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'quit_clicked' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }

    # Icon states
    IDLE_STATE = 0              # Application is currently idle.
    EVENT_FOUND_STATE = 1       # Application has events to show.
    CHECKING_EVENTS_STATE = 2   # Application is checking for events.

    def __init__(self):
        gobject.GObject.__init__(self)
        gtk.StatusIcon.__init__(self)
        self.set_from_stock(gtk.STOCK_HOME)
        self.connect("popup-menu", self.right_click_event)
#        self.connect("activate", self.on_activate)
        self.set_tooltip("PRSpy")

        self.current_state = self.IDLE_STATE;

    def update(self, events):
        self.current_state = self.EVENT_FOUND_STATE
        self._update_icon()

    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()

        force_item = gtk.MenuItem("Force Check")
        quit_item = gtk.MenuItem("Quit")

        force_item.connect("activate", self._emit_force_clicked)
        quit_item.connect("activate", self._emit_quit_clicked)

        menu.append(force_item)
        menu.append(quit_item)

        menu.show_all()

        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self)

    def reset_icon_state(self):
        self.current_state = self.IDLE_STATE
        self._update_icon()

    def _update_icon(self):
        if self.current_state == self.IDLE_STATE:
            self.set_from_stock(gtk.STOCK_HOME)
            self.set_blinking(False)
        elif self.current_state == self.EVENT_FOUND_STATE:
            self.set_from_stock(gtk.STOCK_JUMP_TO)
            self.set_blinking(True)

    def _emit_force_clicked(self, menu):
        self.emit('force_clicked')

    def _emit_quit_clicked(self, menu):
        self.emit('quit_clicked')

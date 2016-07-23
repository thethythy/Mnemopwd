# -*- coding: utf-8 -*-

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import curses
import curses.ascii

from client.util.Configuration import Configuration
from client.uilayer.uicomponents.MetaButtonBox import MetaButtonBox
from client.uilayer.uicomponents.BaseWindow import BaseWindow


class SearchResultPanel(BaseWindow):
    """
    The panel containing search results.
    """

    def __init__(self, parent, h, w, y, x, modal=False, menu=False):
        """Create base window"""
        BaseWindow.__init__(self, parent, h, w, y, x, modal=modal, menu=menu)
        self.intern_pad = curses.newpad(1000, w - 1)
        self.scroll_pos = 0

    def _update_application(self, show):
        """Update application window"""
        if show is True:
            idblock, sib = self.items[self.index].get_data()
            atuple = int(sib['info1'].decode()), sib
            self.parent.update_window("application.editionblock.seteditors", atuple)
        else:
            self.parent.update_window("application.editionblock.cleareditors", None)

    def add_item(self, idblock, sib):
        """Add a component in the window"""
        item = MetaButtonBox(self, len(self.items), 0, sib['info2'].decode(), data=(idblock, sib))
        self.items.append(item)

    def remove_item(self, item_to_remove):
        """Remove an existing component"""
        for i, item in enumerate(self.items):
            if item == item_to_remove:
                self.items[i].close()
                del self.items[i]
                return

    def focus_on(self):
        """This window obtains the focus"""
        if len(self.items) > 0:
            self.parent.focus_off_force(0)
        else:
            curses.ungetch(curses.ascii.ESC)

    def focus_off(self):
        """This window has lost the focus"""
        if len(self.items) > 0:
            self.items[self.index].focus_off()

    def start(self, timeout=-1):
        """See mother class"""
        self.window.timeout(timeout)  # timeout for getch function
        self.window.getch()  # Clear the buffer ?

        # Automatic lock screen
        counter = 0
        timer = Configuration.lock * 60 * 1000  # Timer in ms

        nbitems = len(self.items)
        if nbitems > 0:
            self.items[self.index].focus_on()  # Focus on component at index
            self._update_application(True)  # Update application window

        while True:
            c = self.window.getch()

            # Timeout ?
            if c == -1 and timer > 0:
                counter += 100
                if counter >= timer:
                    self.parent.lock_screen()
                    self.items[self.index].focus_on()
                    counter = 0
            elif c != -1:
                counter = 0

            # Next component
            if c in [curses.KEY_DOWN, curses.ascii.TAB]:
                self.items[self.index].focus_off()
                if self.menu and (self.index + 1) >= nbitems:
                    self._update_application(False)
                    return 1
                self.index = (self.index + 1) % nbitems
                self.items[self.index].focus_on()
                self._update_application(True)  # Update application window

            # Previous component
            elif c in [curses.KEY_UP]:
                self.items[self.index].focus_off()
                if self.menu and (self.index - 1) < 0:
                    self._update_application(False)
                    return -1
                self.index = (self.index - 1) % nbitems
                self.items[self.index].focus_on()
                self._update_application(True)  # Update application window

            # Validation
            elif c in [curses.ascii.CR]:
                self.items[self.index].focus_off()
                return self.items[self.index]

            # Cancel
            elif c in [curses.ascii.ESC] and self.modal:
                self.items[self.index].focus_off()
                self._update_application(False)
                return False

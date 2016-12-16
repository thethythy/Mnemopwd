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

from .Component import Component


class BaseWindow(Component):
    """
    A window without border and without title. It can contain other components.

    KEY_TAB, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN: navigate between components
    ENTER: exit an editable component or execute an actionable component
    shortcuts (Ctrl + key): execute an actionable component
    ESC: close the window
    other keys: start edition of an editable component

    Attribute(s):
    - h: the window height
    - w: the window width
    - window: the curses window
    - items: the ordered list of inner components
    - shortcuts: the ordered list of shortcut keys
    - index: the actual inner component that gets focus
    - menu: the window works like a menu (KEY_LEFT and KEY_RIGHT close the menu)
    - modal: the window is modal window or not
    """

    def __init__(self, parent, h, w, y, x, menu=False, modal=False):
        """Create base window"""
        Component.__init__(self, parent, h, w, y, x, modal=modal)
        self.items = []
        self.shortcuts = []
        self.index = 0
        self.window.keypad(1)
        self.menu = menu

    def start(self, timeout=-1):
        """Start interaction loop of the window"""
        self.window.timeout(timeout)  # timeout for getch function

        nbitems = len(self.items)
        if nbitems > 0:
            self.items[self.index].focus_on()  # Focus on component at index

        reset = False  # Reset timeout
        while True:
            c = self.window.getch()

            # Timeout ?
            if c == -1 and reset is False:
                return 'timeout'
            elif c == -1 and reset is True:
                return 'reset'
            elif c != -1:
                reset = True

            # Next component
            if c in [curses.KEY_DOWN, curses.ascii.TAB]:
                self.items[self.index].focus_off()
                if self.menu and (self.index + 1) >= nbitems:
                    return 1
                self.index = (self.index + 1) % nbitems
                if self.items[self.index].is_editable() or \
                   self.items[self.index].is_actionable():
                    self.items[self.index].focus_on()
                else:
                    curses.ungetch(curses.KEY_DOWN)

            # Previous component
            elif c in [curses.KEY_UP]:
                self.items[self.index].focus_off()
                if self.menu and (self.index - 1) < 0:
                    return -1
                self.index = (self.index - 1) % nbitems
                if self.items[self.index].is_editable() or \
                   self.items[self.index].is_actionable():
                    self.items[self.index].focus_on()
                else:
                    curses.ungetch(curses.KEY_UP)

            # Next actionable component or edit editable component
            elif c in [curses.KEY_LEFT] and self.items[self.index].is_actionable():
                if self.menu:
                    curses.ungetch(curses.KEY_LEFT)
                    return False
                else:
                    curses.ungetch(curses.KEY_UP)

            # Previous actionable component or edit editable component
            elif c in [curses.KEY_RIGHT] and \
                    self.items[self.index].is_actionable():
                if self.menu:
                    curses.ungetch(curses.KEY_RIGHT)
                    return False
                else:
                    curses.ungetch(curses.KEY_DOWN)

            # Validation
            elif c in [curses.ascii.CR]:
                return self.items[self.index]

            # Cancel
            elif c in [curses.ascii.ESC] and self.modal:
                self.items[self.index].focus_off()
                return False

            # Shortcut keys
            elif curses.ascii.isctrl(c):
                c += 64  # Add 64 to get upper key
                for number, shortcut in enumerate(self.shortcuts):
                    if shortcut == chr(c) and \
                            self.items[number].is_actionable():
                        self.items[self.index].focus_off()
                        self.index = number
                        self.items[self.index].focus_on()
                        return self.items[self.index]

            # Other case : start edition of editable components
            else:
                if self.items[self.index].is_editable():
                    self.items[self.index].focus_off()
                    curses.ungetch(c)
                    self.items[self.index].edit()

    def redraw(self):
        """See the mother class"""
        for item in self.items:
            item.redraw()

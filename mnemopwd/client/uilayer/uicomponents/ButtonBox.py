# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
from .Component import Component


class ButtonBox(Component):
    """A simple button text box"""
    
    def __init__(self, parent, y, x, label, shortcut=None, show=True, colour=False):
        self.label = ' ' + label + ' '
        Component.__init__(self, parent, 1, len(self.label) + 1, y, x)
        self.colour = colour
        self.shortcut = shortcut
        self.showOrHide = show
        self.focus = False
        if self.showOrHide:
            self.focus_off()
        
    def focus_on(self):
        """See mother class"""
        self.focus = True
        self.window.addstr(0, 0, self.label,
                           curses.A_BLINK | curses.A_REVERSE | self.colour)
        if self.shortcut:
            self.window.addstr(
                0, self.label.find(self.shortcut), self.shortcut,
                curses.A_UNDERLINE | curses.A_BLINK | curses.A_REVERSE | self.colour)
        self.window.refresh()
        
    def focus_off(self):
        """See mother class"""
        self.focus = False
        self.window.addstr(0, 0, self.label, self.colour)
        if self.shortcut:
            self.window.addstr(
                0, self.label.find(self.shortcut), self.shortcut,
                curses.A_UNDERLINE | self.colour)
        self.window.refresh()

    def has_focus(self):
        """Does the component have the focus"""
        return self.focus

    def move(self, y, x, focus=False):
        """See mother class"""
        self.y = y
        self.x = x
        self.window.erase()
        self._create(focus)

    def show(self):
        """Show the button"""
        self.showOrHide = True
        self.focus_off()

    def hide(self):
        """Hide the button"""
        self.showOrHide = False
        self.window.clear()
        self.window.refresh()

    def close(self):
        """See mother class"""
        if self.showOrHide:
            Component.close(self)

    def redraw(self):
        """See mother class"""
        if self.showOrHide:
            self.focus_off()

    def _create(self, focus):
        """Create the button"""
        self.window = self.parent.window.derwin(
            1, len(self.label) + 1, self.y, self.x)
        if self.showOrHide:
            if focus:
                self.focus_on()
            else:
                self.focus_off()

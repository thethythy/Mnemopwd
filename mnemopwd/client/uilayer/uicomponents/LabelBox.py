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
from .Component import Component


class LabelBox(Component):
    """A simple text widget no editable and no actionable"""

    def __init__(self, parent, y, x, label, show=True):
        Component.__init__(self, parent, 1, len(label) + 1, y, x)
        self.label = label
        self.showOrHide = show
        if show:
            self._create()

    def is_actionable(self):
        """Return False (no actionable)"""
        return False

    def move(self, y, x):
        """See mother class"""
        self.y = y
        self.x = x
        self.window.erase()
        self.window = self.parent.window.derwin(1, len(self.label) + 1, y, x)
        self._create()

    def show(self):
        """Show the button"""
        self.showOrHide = True
        self._create()

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
            self._create()

    def _create(self):
        """Create the widget content"""
        if self.showOrHide:
            self.window.addstr(0, 0, self.label)
            self.window.refresh()

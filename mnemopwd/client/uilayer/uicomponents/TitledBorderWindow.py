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

from .BaseWindow import BaseWindow


class TitledBorderWindow(BaseWindow):
    """
    A window with a border and a title. Subclass of BaseWindow.
    """

    def __init__(self, parent, h, w, y, x, title, modal=False, colourT=False, colourD=False):
        """Create base window"""
        BaseWindow.__init__(self, parent, h, w, y, x, modal=modal)
        self.title = title
        self.colourT = colourT
        self.colourD = colourD
        self._create()

    def redraw(self):
        """See mother class"""
        self._create()
        BaseWindow.redraw(self)

    def close(self):
        """See mother class"""
        if self.modal:
            self.shadows.erase()  # Erase shadows
            self.shadows.refresh()
        BaseWindow.close(self)

    def _create(self):
        self.window.attrset(self.colourD)
        self.window.border()
        self.window.addstr(1, 2, self.title, self.colourT)
        self.window.hline(2, 1, curses.ACS_HLINE, self.w - 2)
        # Add a shadow if it is a modal window
        if self.modal:
            self.shadows = curses.newwin(self.h, self.w + 1, self.y + 1,
                                         self.x + 1)
            self.shadows.attrset(self.colourD)
            self.shadows.addstr(self.h - 1, 0, chr(0x2580)*self.w)  # Horizontal
            for i in range(0, self.h - 1):
                self.shadows.addstr(i, self.w - 1, chr(0x2588))  # Vertical
            self.shadows.refresh()
        self.window.refresh()
        self.window.attrset(0)

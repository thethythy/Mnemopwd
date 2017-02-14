# -*- coding: utf-8 -*-

# Copyright (c) 2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
import math

from .Component import Component


class VertScrollBar(Component):
    """A vertical scrolling bar"""

    def __init__(self, parent, h, y, x):
        """Initialization of a VertScrollBar instance"""
        Component.__init__(self, parent, h, 2, y, x, False)
        self.size = 0  # Vertical length of the scrolling bar
        self.pos = 0  # Position of the scrolling bar
        self.count = 0  # Counter for scrolling up or scrolling down
        self.counter = 0  # Counter for adjusting
        self.content_size = 0  # Save content size for adjusting
        self._create()

    def is_actionable(self):
        """See mother class"""
        return False

    def update(self, content_size):
        """Update scrolling bar size"""
        self.content_size = content_size
        size = math.floor(self.h * self.h / content_size)
        do_redraw = self.size != size

        if size < self.h:
            self.size = size  # New scrolling bar length
        else:
            self.size = 0  # No scrolling bar

        if do_redraw:
            self._create()

    def scroll(self, direction):
        """Try to scrolling up or scrolling down"""
        if self.size > 0:
            # Redraw bottom decoration or not
            self.counter += direction
            do_redraw = self.counter == self.content_size - self.h

            # Redraw scrolling bar or not
            self.count += direction
            pos = self.pos
            if math.fabs(self.count) == math.floor(self.h / self.size):
                pos += direction
                self.count = 0

                pos = max(0, pos)  # Top limit
                pos = min(pos, self.h - self.size)  # Bottom limit
                do_redraw = pos != self.pos
                self.pos = pos

            if do_redraw:
                self._create()

    def redraw(self):
        """See the mother class"""
        self._create()

    def _create(self):
        """Draw the widget content"""
        if self.h >= 2:
            # Draw standard shape
            for i in range(1, self.h - 1):
                self.window.addch(i, 0, curses.ACS_VLINE)  # '|'
            # Draw decorations
            self.window.addstr(0, 0, chr(0x25B2))  # '▲'
            self.window.addstr(self.h - 1, 0, chr(0x25BC))  # '▼'
            # Draw scrolling bar if necessary
            if self.size > 0:
                end = self.pos + self.size + 1
                for i in range(self.pos, end):
                    self.window.addstr(i, 0, chr(0x2588))  # '█'
            # Redraw bottom decoration if necessary
            if self.counter < self.content_size - self.h:
                self.window.addstr(self.h - 1, 0, chr(0x25BC))  # '▼'
            # Finally refresh window
            self.window.refresh()

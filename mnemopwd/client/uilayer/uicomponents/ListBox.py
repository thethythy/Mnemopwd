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
import curses.ascii

from .BaseWindow import BaseWindow
from .Component import Component
from .VertScrollBar import VertScrollBar
from .MetaButtonBox import MetaButtonBox


class ListBox(BaseWindow):
    """
    A simple list box for selecting one item.
    A vertical scroll bar is visible if necessary.
    """

    def __init__(self, parent, h, w, y, x, colourB=False, colourD=False):
        """Create base window"""
        BaseWindow.__init__(self, parent, h, w, y, x, modal=True, menu=True)
        self.colourB = colourB
        self.colourD = colourD
        self.listener = None  # The listener of any changes
        self.scroll_bar = None  # Vertical scroll bar widget
        self.scroll_pos = 0  # Initial scroll bar position

    def _update_parent(self):
        """Update parent window"""
        if self.listener is not None:
            self.listener.update(self.items[self.index])

    def _scroll_items(self, d):
        """Scroll up or scroll down items"""
        # Hide actual visible items
        for i in range(self.index, self.index + (- d * self.h), - d):
            self.items[i].hide()
        # Move all items
        for item in self.items:
            item.move(item.y - d, 0)
        # Show only visible items
        for i in range(self.index + d, self.index + d + (- d * self.h), - d):
            self.items[i].show()

    def _half_scroll_up_items(self, pos):
        """Scroll up items only from a certain position"""
        # Hide some visible items
        end = min(len(self.items), pos + self.h - self.scroll_pos)
        for i in range(pos, end):
            self.items[i].hide()
        # Move some items
        for i in range(pos, len(self.items)):
            self.items[i].move(self.items[i].y - 1, 0)
        # Show some visible items
        for i in range(pos, end):
            self.items[i].show()

    def set_listener(self, listener):
        """Set the listener of changes"""
        if isinstance(listener, Component):
            self.listener = listener

    def add_item(self, label, idx, data=False, scroll=True):
        """Add a component in the window"""
        # Add a button (visible or not visible)
        nbitems = len(self.items)
        label = label[:self.w - 5]
        show = (nbitems + 1) <= self.h
        self.items.append(MetaButtonBox(self, nbitems, 0, label, show=show,
                                        data=(idx, data), colour=self.colourB))

        # Show and/or update scrolling bar
        show = (nbitems + 1) > self.h
        if scroll and show:
            if self.scroll_bar is None:
                self.scroll_bar = VertScrollBar(self, self.h, 0, self.w - 2,
                                                colour=self.colourD)
            self.scroll_bar.update(nbitems + 1)

    def update_item(self, idx, data):
        """Update a component"""
        for item in self.items:
            idx2, old = item.get_data()
            if idx2 == idx:
                item.set_data((idx, data))
                break

    def remove_item(self, idx):
        """Remove an existing component"""
        for i, item in enumerate(self.items):
            idx2, old = item.get_data()
            if idx2 == idx:
                # Close item
                if item.showOrHide:
                    item.close()
                    # Update index and scroll position
                    if self.items[self.index] == item:
                        old_index = self.index
                        self.index = min(self.index, len(self.items) - 2)
                        if self.index != old_index:
                            self.scroll_pos = max(0, self.scroll_pos - 1)
                # Remove item from the list
                del self.items[i]
                # Scroll up by one from position i
                self._half_scroll_up_items(i)
                if self.scroll_bar is not None:
                    if len(self.items) > self.h:
                        self.scroll_bar.update(len(self.items))
                    else:
                        self.scroll_bar.update(1)  # Hide scroll bar
                break

    def clear_content(self):
        """Delete all components"""
        # Close scrolling bar
        self.scroll_bar = None
        self.scroll_pos = 0

        # Delete items
        self.items = []
        self.index = 0

        # Clear window
        self.window.clear()
        self.window.refresh()

    def focus_on(self):
        """This window obtains the focus"""
        if len(self.items) > 0:
            curses.ungetch(curses.ascii.CR)  # Simulate activation
        else:
            curses.ungetch(curses.ascii.ESC)  # Simulate deactivation

    def focus_off(self):
        """This window has lost the focus"""
        if len(self.items) > 0:
            self.items[self.index].focus_off()

    def start(self, timeout=-1):
        """See mother class"""
        self.window.timeout(timeout)  # timeout for getch function

        if len(self.items) > 0:
            self.items[self.index].focus_on()  # Focus on component at index
            self._update_parent()

        while True:
            c = self.window.getch()

            # Next component
            if c in [curses.KEY_DOWN, curses.ascii.TAB]:
                self.items[self.index].focus_off()
                # Bottom reached
                if self.menu and (self.index + 1) >= len(self.items):
                    self._update_parent()
                    return 1
                # Down by one
                if (self.index + 1) < len(self.items) and \
                   (self.scroll_pos + 1) == self.h:
                    self._scroll_items(1)
                    self.scroll_bar.scroll(1)
                # Normal behaviour
                self.scroll_pos = min(self.h - 1, self.scroll_pos + 1)
                self.index = (self.index + 1) % len(self.items)
                self.items[self.index].focus_on()
                self._update_parent()

            # Previous component
            elif c in [curses.KEY_UP]:
                self.items[self.index].focus_off()
                # Top reached
                if self.menu and (self.index - 1) < 0:
                    self._update_parent()
                    return -1
                # Up by one
                if (self.index - 1) >= 0 and self.scroll_pos == 0:
                    self._scroll_items(-1)
                    self.scroll_bar.scroll(-1)
                # Normal behaviour
                self.scroll_pos = max(0, self.scroll_pos - 1)
                self.index = (self.index - 1) % len(self.items)
                self.items[self.index].focus_on()
                self._update_parent()

            # Validation
            elif c in [curses.ascii.CR]:
                self.items[self.index].focus_off()
                return self.items[self.index]

            # Cancel
            elif c in [curses.ascii.ESC] and self.modal:
                self.items[self.index].focus_off()
                self._update_parent()
                return False

    def close(self):
        """Close the component"""
        # Clear the content
        self.window.erase()
        self.window.refresh()

    def redraw(self):
        """See the mother class"""
        BaseWindow.redraw(self)
        if self.scroll_bar is not None:
            self.scroll_bar.redraw()

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

"""Simple text editing widget (copy of the official file but with
character > 127, a software cursor and without insert mode)"""

import curses
import curses.ascii


class TextEditor:
    """Editing widget using the interior of a window object.
     Supports the following key bindings:

    Ctrl-A   Go to left edge of window.
    Ctrl-B   Cursor left, wrapping to previous line if appropriate.
    Ctrl-D   Delete character under cursor.
    Ctrl-E   Go to right edge (stripspaces off) or end of line (stripspaces on).
    Ctrl-F   Cursor right, wrapping to next line when appropriate.
    Ctrl-G   Terminate, returning the window contents.
    Ctrl-H   Delete character backward.
    Ctrl-J   Terminate if the window is 1 line, otherwise insert newline.
    Ctrl-K   If line is blank, delete it, otherwise clear to end of line.
    Ctrl-L   Refresh screen.
    Ctrl-N   Cursor down; move down one line.
    Ctrl-O   Insert a blank line at cursor location.
    Ctrl-P   Cursor up; move up one line.

    Move operations do nothing if the cursor is at an edge where the movement
    is not possible.  The following synonyms are supported where possible:

    KEY_LEFT = Ctrl-B, KEY_RIGHT = Ctrl-F, KEY_UP = Ctrl-P, KEY_DOWN = Ctrl-N
    KEY_BACKSPACE = Ctrl-h
    """
    def __init__(self, win):
        self.win = win
        (self.maxy, self.maxx) = win.getmaxyx()
        self.maxy -= 1
        self.maxx -= 2
        self.stripspaces = 1
        win.keypad(1)

    def _end_of_line(self, y):
        """Go to the location of the first blank on the given line,
        returning the index of the last non-blank character."""
        last = self.maxx
        while True:
            if curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last+1)
                break
            elif last == 0:
                break
            last -= 1
        return last

    def _show_cursor(self):
        """Insert a software cursor at the actual position"""
        self.win.addch('_', curses.A_BLINK)
        (y, x) = self.win.getyx()
        self.win.move(y, x - 1)

    def _insert_printable_char(self, ch):
        # The try-catch ignores the error we trigger from some curses
        # versions by trying to write into the lowest-rightmost spot
        # in the window.
        try:
            self.win.addch(ch)
            self._show_cursor()  # Add this
        except curses.error:
            pass

    def populate(self, value):
        """Preset value in the editor"""
        self.win.move(0, 0)
        for ch in value:
            try:
                self.win.addch(ch)
            except curses.error:
                pass

    def do_command(self, ch):
        """Process a single editing command."""
        (y, x) = self.win.getyx()
        if ch == curses.ascii.SOH:                             # ^a
            self.win.move(y, 0)
        elif ch in (curses.ascii.STX, curses.KEY_LEFT, curses.ascii.BS,
                    curses.KEY_BACKSPACE):
            if x > 0:
                self.win.move(y, x-1)
            elif y == 0:
                pass
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            else:
                self.win.move(y-1, self.maxx)
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
                self._show_cursor()  # Add this
        elif ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
        elif ch == curses.ascii.ENQ:                           # ^e
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x < self.maxx:
                self.win.move(y, x+1)
            elif y == self.maxy:
                pass
            else:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.BEL:                           # ^g
            self.win.clrtoeol()
            return 0
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                self.win.clrtoeol()
                return 0
            elif y < self.maxy:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y < self.maxy:
                self.win.move(y+1, x)
                if x > self._end_of_line(y+1):
                    self.win.move(y+1, self._end_of_line(y+1))
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                if x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))
        else:
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
        return 1

    def gather(self):
        """Collect and return the contents of the window."""
        result = ""
        for y in range(self.maxy+1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            if stop == 0 and self.stripspaces:
                continue
            for x in range(self.maxx+1):
                if self.stripspaces and x >= stop:  # A bug corrected here
                    break
                result += chr(self.win.inch(y, x))
            if self.maxy > 0:
                result += "\n"
        return result

    def edit(self, validate=None):
        """Edit in the widget window and collect the results."""
        self._show_cursor()  # Add this
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.win.refresh()
        return self.gather()

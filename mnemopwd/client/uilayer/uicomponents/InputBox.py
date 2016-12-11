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
from .TextEditor import TextEditor
from .SecretTextEditor import SecretTextEditor
from .Component import Component


class InputBox(Component):
    """
    A simple text editor with a border line

    Attributes:
    - value: the output text after edition
    - shortcuts: list of shortcut keys for ending edition
    - secret: is it a secret text?
    """

    def __init__(self, parent, h, w, y, x, shortcuts=None, secret=False,
                 show=True, option=False):
        """Create a input text box"""
        Component.__init__(self, parent, h, w, y, x)
        if show:
            self.window.border()
            self.window.refresh()
        self.editorbox = self.window.derwin(1, w - 4, 1, 2)
        if not secret:
            self.editor = TextEditor(self.editorbox)
        else:
            self.editor = SecretTextEditor(self.editorbox)
        self.value = None
        self.shortcuts = shortcuts
        self.option = option
        self.showOrHide = show

        # Cursor position
        self.cursor_y = 0
        self.cursor_x = 0

        # Cursor shape
        self.cursor_shape = '█'  # Like a terminal cursor

    def is_editable(self):
        """This component is editable"""
        return True

    def is_actionable(self):
        """Return True by default (actionable)"""
        return False

    def focus_on(self):
        """See mother class"""
        self.editorbox.addstr(self.cursor_y, self.cursor_x, self.cursor_shape,
                              curses.A_BLINK)
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.refresh()

    def focus_off(self):
        """See mother class"""
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.clrtoeol()
        self.editorbox.refresh()

    def clear(self):
        """Clean up the editor content"""
        self.value = None
        self.cursor_x = 0
        self.focus_off()

    def show(self):
        """Show the editor"""
        self.showOrHide = True
        if self.value is not None:
            self.editor.populate(self.value)
            self.cursor_x = len(self.value)
        self.window.border()
        self.window.refresh()

    def hide(self):
        """Hide the editor"""
        self.showOrHide = False
        self.window.clear()
        self.window.refresh()

    def redraw(self):
        """Redraw the editor"""
        if self.showOrHide:
            if self.value is not None:
                self.editor.populate(self.value)
                self.cursor_x = len(self.value)
            self.window.border()
            self.window.refresh()

    def _controller_(self, ch):
        """Control if the character is a control key"""
        if ch in [curses.KEY_UP, curses.KEY_DOWN, curses.ascii.TAB,
                  curses.ascii.CR, curses.ascii.ESC, curses.KEY_MOUSE]:
            curses.ungetch(ch)
            return curses.ascii.NL
        elif ch in [curses.ascii.DEL]:
            return curses.ascii.BS
        elif curses.ascii.isctrl(ch):
            if chr(ch + 64) in self.shortcuts:
                curses.ungetch(ch)
                return curses.ascii.NL
        else:
            return ch

    def edit(self):
        """Start editing operation"""
        try:
            curses.curs_set(2)
        except curses.error:
            pass
        result = self.editor.edit(self._controller_)
        if result != self.value:
            if result != "":
                self.value = result
                self.cursor_x = len(result)
            else:
                self.value = None
                self.cursor_x = 0
        try:
            curses.curs_set(0)
        except curses.error:
            pass

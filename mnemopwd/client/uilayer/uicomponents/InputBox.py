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
from curses.textpad import Textbox
from client.uilayer.uicomponents.Component import Component

class InputBox(Component):
    """A simple text editor with a border line"""
    
    def __init__(self, wparent, h, w, y, x):
        """Create a input text box"""
        Component.__init__(self, wparent, y, x)
        self.panel = wparent.derwin(h, w, y, x)
        self.panel.border()
        self.editorbox = self.panel.derwin(1, w - 4, 1, 2)
        self.editor = Textbox(self.editorbox)
        self.value = None
        
    def isEditable(self):
        """This component is editable"""
        return True
        
    def isActionnable(self):
        """Return True by default (actionnable)"""
        return False
        
    def focusOn(self):
        """See mother class"""
        self.editorbox.addstr(self.cursor_y, self.cursor_x, ' ', curses.A_REVERSE)
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.refresh()
        
    def focusOff(self):
        """See mother class"""
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.clrtoeol()
        self.editorbox.refresh()
        
    def enclose(self, y, x):
        """See mother class"""
        return self.editorbox.enclose(y, x)
        
    def clear(self):
        self.value = None
        self.cursor_x = 0
        self.focusOff()
    
    @staticmethod
    def _controller_(ch):
        if ch in [curses.KEY_UP, curses.KEY_DOWN, curses.ascii.TAB, curses.ascii.CR, 
                  curses.ascii.ESC, curses.KEY_MOUSE]:
            curses.ungetch(ch)
            return curses.ascii.NL
        elif ch in [curses.ascii.DEL]:
            return curses.ascii.BS
        else:
            return ch
        
    def edit(self):
        try: curses.curs_set(1)
        except curses.error: pass
        result = self.editor.edit(InputBox._controller_)
        if result != self.value:
            if result != "":
                self.value = result
                self.cursor_x = len(result) - 1
            else:
                self.value = None
                self.cursor_x = 0
        try: curses.curs_set(0)
        except curses.error: pass


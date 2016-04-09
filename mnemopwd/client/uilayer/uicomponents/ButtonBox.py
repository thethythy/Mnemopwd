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
from client.uilayer.uicomponents.Component import Component

class ButtonBox(Component):
    """A simple button text box"""
    
    def __init__(self, wparent, y, x, label):
        Component.__init__(self, wparent, y, x)
        self.label = '[' + label + ']'
        self.button = wparent.derwin(1, len(label), y, x)
        self.parent.addstr(y, x, self.label, curses.A_REVERSE)
        self._cur_y = y
        self._cur_x = x
        
    def focusOn(self):
        """See mother class"""
        self.parent.addstr(self.cursor_y, self.cursor_x, self.label, curses.A_BLINK | curses.A_REVERSE)
        self.parent.refresh()
        
    def focusOff(self):
        """See mother class"""
        self.parent.addstr(self.cursor_y, self.cursor_x, self.label, curses.A_REVERSE)
        self.parent.refresh()
        
    def enclose(self, y, x):
        """See mother class"""
        return self.button.enclose(y, x)


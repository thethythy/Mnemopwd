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

class BaseWindow(Component):
    """
    A window without border and without title. It can contain other components.
    
    Attributs:
    - h: the window height
    - w: the window width
    - window: the curses window
    - items: the ordered list of inner components
    - shortcuts: the ordered list of shortcut keys
    - index: the actual inner component that gets focus
    """
    
    def __init__(self, wparent, h, w, y, x):
        """Create base window"""
        Component.__init__(self, wparent, y, x)
        self.h = h
        self.w = w
        self.window = curses.newwin(h, w, y, x)
        self.items = []
        self.shortcuts = []
        self.index = 0
        self.window.keypad(1)
        
    def start(self):
        """Start interaction loop of the window"""
        curses.nonl()
        
        self.items[self.index].focusOn() # Focus on component at index
        
        while True:
            c = self.window.getch()
            
            # Mouse event
            if c == curses.KEY_MOUSE:
                id, x, y, z, bstate = curses.getmouse()
                for number, item in enumerate(self.items):
                    if item.enclose(y, x):
                        self.items[self.index].focusOff()
                        self.index = number
                        self.items[self.index].focusOn()
                        if self.items[self.index].isActionnable():
                            return self.items[self.index]
                        else: break
            
            # Next component
            elif c in [curses.KEY_DOWN, curses.ascii.TAB] :
                self.items[self.index].focusOff()
                self.index = (self.index + 1) % len(self.items)
                self.items[self.index].focusOn()
            
            # Previous component
            elif c in [curses.KEY_UP]:
                self.items[self.index].focusOff()
                self.index = (self.index - 1) % len(self.items)
                self.items[self.index].focusOn()
            
            # Next actionnable component or edit editable component
            elif c in [curses.KEY_LEFT] and self.items[self.index].isActionnable():
                curses.ungetch(curses.KEY_UP)
            
            # Previous actionnable component or edit editable component
            elif c in [curses.KEY_RIGHT] and self.items[self.index].isActionnable():
                curses.ungetch(curses.KEY_DOWN)
            
            # Validation
            elif c in [curses.ascii.CR]:
                if self.items[self.index].isEditable():
                    curses.ungetch(curses.KEY_DOWN)
                elif self.items[self.index].isActionnable():
                    return self.items[self.index]
            
            # Cancel
            elif c in [curses.ascii.ESC] :
                return False
                
            # Shortcut keys
            elif curses.ascii.isctrl(c):
                c += 64 # Add 64 to get upper key
                for number, shortcut in enumerate(self.shortcuts):
                    if shortcut == chr(c) and self.items[number].isActionnable():
                        self.items[self.index].focusOff()
                        self.index = number
                        self.items[self.index].focusOn()
                        return self.items[self.index]
            
            # Other case : start edition of editable component
            else:
                if self.items[self.index].isEditable():
                    self.items[self.index].focusOff()
                    curses.ungetch(c)
                    self.items[self.index].edit()
                    
    def close(self):
        """Close the window"""
        curses.nl()
        self.window.clear()
        self.window.refresh()


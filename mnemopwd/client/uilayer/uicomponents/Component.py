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


class Component:
    """Abstract component"""
    
    def __init__(self, parent, h, w, y, x, modal=False):
        """
        Create a component at (y, x) position of parent window
        with size (h,w) and with parent as parent component
        """
        self.parent = parent
        self.y = y
        self.x = x
        self.h = h
        self.w = w
        self.modal = modal
        
        # Create a new window
        if isinstance(self.parent, Component):
            self.window = self.parent.window.derwin(h, w, y, x)
        elif parent is None:
            self.window = curses.newwin(h, w, y, x)
        else:
            self.window = self.parent

        # Clear the content to have an empty window
        self.window.clear()
        self.window.refresh()

    def is_editable(self):
        """Return False by default (not editable)"""
        return False
        
    def is_actionable(self):
        """Return True by default (actionable)"""
        return True
    
    def focus_on(self):
        """This component obtains the focus"""
        pass
        
    def focus_off(self):
        """This component has lost the focus"""
        pass

    def move(self, y, x, focus=False):
        """Move the component to a new location"""
        pass

    def redraw(self):
        """Redraw the component's content"""
        pass

    def close(self):
        """Close the component"""
        # Clear the content
        self.window.erase()
        self.window.refresh()

        # Restore the old screen if needed
        if self.modal and isinstance(self.parent, Component):
            self.parent.redraw()

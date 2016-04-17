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

class Component():
    """Abstract component"""
    
    def __init__(self, wparent, y, x):
        self.parent = wparent
        self.y = y
        self.x = x
        self._cur_y = 0
        self._cur_x = 0
    
    @property
    def cursor_y(self):
        return self._cur_y
    
    @cursor_y.setter
    def cursor_y(self, value):
        self._cur_y = value
    
    @property
    def cursor_x(self):
        return self._cur_x
    
    @cursor_x.setter
    def cursor_x(self, value):
        self._cur_x = value
    
    def isEditable(self):
        """Return False by default (not editable)"""
        return False
        
    def isActionnable(self):
        """Return True by default (actionnable)"""
        return True
    
    def focusOn(self):
        """This component obtains the focus"""
        pass
        
    def focusOff(self):
        """This component losts the focus"""
        pass
        
    def enclose(self, y, x):
        """Does this component enclose the (y,x) coordinate"""
        return False
        
    def move(self, y, x, focus=False):
        """Move the component to a new location"""
        pass


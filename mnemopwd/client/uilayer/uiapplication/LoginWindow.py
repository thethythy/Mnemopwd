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

from client.uilayer.uicomponents.TitledBorderWindow import TitledBorderWindow
from client.uilayer.uicomponents.InputBox import InputBox
from client.uilayer.uicomponents.ButtonBox import ButtonBox

class LoginWindow(TitledBorderWindow):
    """
    The login window: get the login/password user credentials
    """
    
    def __init__(self):
        """Create the window"""
        size_y = 14
        size_x = 60
        
        TitledBorderWindow.__init__(self, None, size_y, size_x,
                                    int(curses.LINES / 2) - int(size_y / 2),
                                    int(curses.COLS / 2) - int(size_x / 2),
                                    "Connection window")
        
        self.window.addstr(5, 2, "Login")
        self.window.addstr(8, 2, "Password")
        
        # Ordered list of shortcut keys
        self.shortcuts = ['', '', 'N', 'L', 'A']
        
        # Editable components
        self.logineditor = InputBox(self.window, 3, size_x - 15, 5 - 1, 12, self.shortcuts)
        self.passeditor = InputBox(self.window, 3, size_x - 15, 8 - 1, 12, self.shortcuts) 
        
        # Actionnable components
        self.connectButton = ButtonBox(self.window, 11, 7, "Connect", 'N')
        self.clearButton = ButtonBox(self.window, 11, 27, "Clear", 'L')
        self.cancelButton = ButtonBox(self.window, 11, 47, "Cancel", 'A')
        
        # Ordered list of components
        self.items = [self.logineditor, self.passeditor, self.connectButton, 
                      self.clearButton, self.cancelButton]
        
        self.window.refresh()
        
    def start(self):
        while True:
            result = TitledBorderWindow.start(self) # Default controller
            
            # Cancel login window
            if result == False or result == self.cancelButton:
                self.close()
                return False, False
            # Clear all input boxes
            elif result == self.clearButton:
                self.logineditor.clear()
                self.passeditor.clear()
                self.clearButton.focusOff()
                self.index = 0
            # Try to return login and password
            elif result == self.connectButton:
                self.connectButton.focusOff()
                if self.logineditor.value is None :
                    self.index = 0
                elif self.passeditor.value is None :
                    self.index = 1
                else:
                    self.close()
                    return self.logineditor.value, self.passeditor.value

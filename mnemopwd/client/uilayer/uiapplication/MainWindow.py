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

from client.util.Configuration import Configuration
from client.uilayer.uicomponents.BaseWindow import BaseWindow
from client.uilayer.uicomponents.ButtonBox import ButtonBox
from client.uilayer.uiapplication.LoginWindow import LoginWindow

class MainWindow(BaseWindow):
    """
    The main window of the client application
    """
    
    def __init__(self, corefacade):
        """Create the window"""
        BaseWindow.__init__(self, None, curses.LINES, curses.COLS, 0, 0)
        self.facade = corefacade # Reference on core layer facade
        
        # Menu zone
        self.window.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.window.addstr(0, curses.COLS - len(message) - 1, message)
        self.window.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.window.addch(1, curses.COLS - len(message) - 3 , curses.ACS_BTEE)
        self.window.refresh()
        
        self.searchButton = ButtonBox(self.window, 0, 0, "Search", shortcut='E')
        self.newButton = ButtonBox(self.window, 0, 8, "New", shortcut='N')
        self.loginButton = ButtonBox(self.window, 0, 12, "Login", shortcut='L')
        self.exitButton = ButtonBox(self.window, 0, 18, "Quit", shortcut='U')
        
        # Ordered list of shortcut keys
        self.shortcuts = ['E', 'N', 'L', 'U']
        
        # Ordered list of components
        self.items = [self.searchButton, self.newButton, self.loginButton, self.exitButton]
        
        # Status window
        self.statscr = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.statscr.attrset(curses.A_DIM)
        self.statscr.refresh()
        
    def _getCredentials(self):
        """Get login/password"""
        connected = False
        login, passwd = LoginWindow().start()
        if (login != False):
            self.facade.setCredentials(login, passwd)
            login = passwd = "                            "
            connected = True
        return connected
        
    def start(self):
        # Get login/password
        connected = self._getCredentials()
        
        while True:
            # Interaction loop
            result = BaseWindow.start(self)
            
            # Try a new connection
            if result == self.loginButton:
                if not connected:
                    self.loginButton.focusOff()
                    connected = self._getCredentials()
            
            # Quit application 
            elif result == False or result == self.exitButton:
                self.close()
                break
        
    def update_status(self, value):
        """Update the status window content"""
        currenty, currentx = curses.getsyx() # Save current cursor position
        self.statscr.move(1, 0)
        self.statscr.clrtoeol()
        self.statscr.addstr(value)
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position

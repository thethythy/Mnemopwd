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
from client.uilayer.uiapplication.EditionWindow import EditionWindow
from client.uilayer.uiapplication.SearchWindow import SearchWindow
from client.uilayer.uiapplication.CreateMenu import CreateMenu

class MainWindow(BaseWindow):
    """
    The main window of the client application
    """
    
    def __init__(self, facade):
        """Create the window"""
        BaseWindow.__init__(self, None, curses.LINES - 2, curses.COLS, 0, 0)
        self.uifacade = facade # Reference on ui layer facade
        self.connected = False # Login state
        
        # Menu zone
        self.window.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.window.addstr(0, curses.COLS - len(message) - 1, message)
        self.window.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.window.addch(1, curses.COLS - len(message) - 3 , curses.ACS_BTEE)
        self.window.refresh()
        
        self.searchButton = ButtonBox(self, 0, 0, "Search", shortcut='E')
        self.newButton = ButtonBox(self, 0, 9, "New", shortcut='N')
        self.loginButton = ButtonBox(self, 0, 15, "Login", shortcut='L')
        self.exitButton = ButtonBox(self, 0, 23, "Quit", shortcut='U')
        
        # Ordered list of shortcut keys
        self.shortcuts = ['E', 'N', 'L', 'U']
        
        # Ordered list of components
        self.items = [self.searchButton, self.newButton, self.loginButton, self.exitButton]
        
        # Edition window
        self.editscr = EditionWindow(self, curses.LINES - 4, int(curses.COLS * 2/3), 2, int(curses.COLS * 1/3), "Edition")
        
        # Search window
        self.searchscr = SearchWindow(self, curses.LINES - 4, int(curses.COLS * 1/3), 2, 0, "Search")
        
        # Status window
        self.statscr = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.statscr.attrset(curses.A_DIM)
        self.statscr.refresh()
        
    def _getCredentials(self):
        """Get login/password"""
        self.update_status('Please start a connection')
        login, passwd = LoginWindow(self).start()
        if (login != False):
            self.uifacade.inform("connection.open.credentials", (login, passwd))
            self.window.addstr(1, 0, login+passwd)
            login = passwd = "                            "
            
    def start(self):
        # Get login/password
        self._getCredentials()
        
        while True:
            # Interaction loop
            result = BaseWindow.start(self)
            
            # Try a new connection or close connection
            if result == self.loginButton:
                if not self.connected:
                    self.loginButton.focusOff()
                    self._getCredentials()
                else:
                    self.uifacade.inform("connection.close", None)
                    
            # Create a new entry
            elif result == self.newButton:
                if self.connected:
                    self.newButton.focusOff()
                    result = CreateMenu(self, Configuration.btypes, 2, 9).start()
                    if result:
                        self.update_status((Configuration.btypes[str(result)])["name"])
                else:
                    self.update_status('Please start a connection')
            
            # Quit application 
            elif result == False or result == self.exitButton:
                if self.connected: self.uifacade.inform("connection.close", None)
                self.close()
                break
    
    def update_window(self, property, value):
        """Update the main window content"""
        if property == "connection.state.login":
            self.connected = True
            self.loginButton.setLabel("Logout", self.loginButton == self.items[self.index])
            self.exitButton.move(0, 24, self.exitButton == self.items[self.index])
            self.update_status(value)
        if property == "connection.state.logout":
            self.connected = False
            self.loginButton.setLabel("Login", self.loginButton == self.items[self.index])
            self.exitButton.move(0, 23, self.exitButton == self.items[self.index])
            self.update_status(value)
        if property == "connection.state.error":
            self.connected = False
            self.loginButton.setLabel("Login", self.loginButton == self.items[self.index])
            self.exitButton.move(0, 23, self.exitButton == self.items[self.index])
            self.update_status(value)
            curses.flash()
    
    def update_status(self, value):
        """Update the status window content"""
        currenty, currentx = curses.getsyx() # Save current cursor position
        self.statscr.move(1, 1)
        self.statscr.clrtoeol()
        if self.connected:
            self.statscr.addstr("-O-")
        else:
            self.statscr.addstr("-||-")
        self.statscr.addch(0, 6, curses.ACS_TTEE)
        self.statscr.addch(1, 6, curses.ACS_VLINE)
        self.statscr.addstr(1, 8, value)
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position
        
    def redraw(self):
        """See mother class"""
        self.editscr.redraw()
        self.searchscr.redraw()
        BaseWindow.redraw(self)
        
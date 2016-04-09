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

from threading import Thread
import locale
import curses

from client.util.funcutils import Observer
from client.util.Configuration import Configuration

from client.uilayer.uicomponents.Component import Component
from client.uilayer.uicomponents.InputBox import InputBox
from client.uilayer.uicomponents.ButtonBox import ButtonBox
from client.uilayer.uicomponents.TitledBorderWindow import TitledBorderWindow


"""
Standard curses user interface.
"""

locale.setlocale(locale.LC_ALL, '') # Set locale setting
encoding = locale.getpreferredencoding() # Get locale encoding

class LoginWindow(TitledBorderWindow):
    """
    The login window: get the login/password user credentials
    """
    
    def __init__(self):
        """Create the window"""
        size_y = 14
        size_x = 60
        
        TitledBorderWindow.__init__(self, size_y, size_x,
                                    int(curses.LINES / 2) - int(size_y / 2),
                                    int(curses.COLS / 2) - int(size_x / 2),
                                    "Connection window")
        
        self.window.addstr(5, 2, "Login")
        self.window.addstr(8, 2, "Password")
        
        # Editable components
        self.logineditor = InputBox(self.window, 3, size_x - 15, 5 - 1, 12)
        self.passeditor = InputBox(self.window, 3, size_x - 15, 8 - 1, 12) 
        
        # Actionnable components
        self.connectButton = ButtonBox(self.window, 11, 7, "Connect")
        self.clearButton = ButtonBox(self.window, 11, 27, "Clear")
        self.cancelButton = ButtonBox(self.window, 11, 47, "Cancel")
        
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

class ClientUI(Thread, Observer):
    """
    The default client user interface (UI).
    
    Attribut(s):
    - facade: the facade of the domain layer
    - stdscr: the main window of the UI
    - menuscr: the menu window at the top line of the UI
    - statscr: the status window at the bottom line of the UI
    
    Method(s):
    - stop: stop the interaction loop
    - run: start the interaction loop
    - update: update the UI (implementation of the Observer class method)
    """

    def __init__(self, facade):
        """Create an initialize UI"""
        Thread.__init__(self)
        Observer.__init__(self)
        
        self.facade = facade # Store the facade of the domain layer
        
        # Main window
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.noecho() 
        try: curses.curs_set(0)
        except: pass
        curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON2_CLICKED | 
                         curses.BUTTON3_CLICKED | curses.BUTTON4_CLICKED)
        
        # Menu window
        self.menuscr = curses.newwin(2, curses.COLS, 0, 0)
        self.menuscr.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.menuscr.addstr(0, curses.COLS - len(message) - 1, message.encode(encoding))
        self.menuscr.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.menuscr.addch(1, curses.COLS - len(message) - 3 , curses.ACS_BTEE)
    
        self.menuscr.addstr(0, 0, "S".encode(encoding), curses.A_UNDERLINE)
        self.menuscr.addstr(0, 1, "earch".encode(encoding))
        self.menuscr.addstr(0, 7, "N".encode(encoding), curses.A_UNDERLINE)
        self.menuscr.addstr(0, 8, "ew".encode(encoding))
        self.menuscr.addstr(0, 11, "L".encode(encoding), curses.A_UNDERLINE)
        self.menuscr.addstr(0, 12, "ogin".encode(encoding))
        self.menuscr.addstr(0, 17, "Q".encode(encoding), curses.A_UNDERLINE)
        self.menuscr.addstr(0, 18, "uit".encode(encoding))
        self.menuscr.refresh()
        
        # Status window
        self.statscr = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.statscr.attrset(curses.A_DIM)
        self.statscr.refresh()

    def stop(self):
        """Stop UI and return to normal interaction"""
        curses.nocbreak()
        self.stdscr.keypad(False)
        try: curses.curs_set(2)
        except: pass
        curses.echo()
        curses.endwin()

    def run(self):
        """Start the loop interaction"""
        
        # Get login/password
        login, passwd = LoginWindow().start()
        if (login != False):
            #self.facade.setCredentials(login, passwd)
            #login = passwd = "                            "
            pass
        
        # Interaction loop
        while True:
            c = self.statscr.getch()
            if c == ord('q'):
                self.facade.stop() # Close the domain layer
                break  # Exit the interaction loop

    def update(self, property, value):
        """Implementation of the method of the class Observer."""
        if property == "connection.state":
            self._update_status(value)
            
    def _update_status(self, value):
        """Update the status window content"""
        currenty, currentx = curses.getsyx() # Save current cursor position
        self.statscr.move(1, 0)
        self.statscr.clrtoeol()
        self.statscr.addstr(value.encode(encoding))
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position


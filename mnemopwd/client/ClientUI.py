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
#import locale
import curses
from curses.textpad import Textbox

from client.util.funcutils import Observer
from client.util.Configuration import Configuration

"""
Standard curses user interface.
"""

class Component():
    """Abstract component"""
    
    def __init__(self, wparent, y, x):
        self.parent = wparent
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
    
    def focusOn(self):
        """This component obtains the focus"""
        pass
        
    def focusOff(self):
        """This component losts the focus"""
        pass

class InputBox(Component):
    """A simple text editor with a border line"""
    
    def __init__(self, wparent, h, w, y, x):
        """Create a input text box"""
        Component.__init__(self, wparent, y, x)
        self.panel = wparent.derwin(h, w, y, x)
        self.panel.border()
        self.editorbox = self.panel.derwin(1, w - 4, 1, 2)
        self.editor = Textbox(self.editorbox)
        
    def isEditable(self):
        """This component is editable"""
        return True
        
    def focusOn(self):
        """See mother class"""
        self.editorbox.addstr(self.cursor_y, self.cursor_x, '_', curses.A_BLINK)
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.refresh()
        
    def focusOff(self):
        """See mother class"""
        self.editorbox.move(self.cursor_y, self.cursor_x)
        self.editorbox.clrtoeol()
        self.editorbox.refresh()

class ButtonBox(Component):
    """A simple button text box"""
    
    def __init__(self, wparent, y, x, label):
        Component.__init__(self, wparent, y, x)
        self.label = '[' + label + ']'
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

class LoginWindow():
    """
    The login window: get the login/password user credentials
    """
    
    def __init__(self):
        """Create the window"""
        size_y = 14
        size_x = 60
        
        self.loginscr = curses.newwin(size_y, size_x,
                                      int(curses.LINES / 2) - int(size_y / 2),
                                      int(curses.COLS / 2) - int(size_x / 2))
        self.loginscr.border()
        self.loginscr.addstr(1, 2, "Connection window")
        self.loginscr.hline(2,1, curses.ACS_HLINE, size_x - 2)
        self.loginscr.addstr(5, 2, "Login")
        self.loginscr.addstr(8, 2, "Password")
        
        self.logineditor = InputBox(self.loginscr, 3, size_x - 15, 5 - 1, 12)
        self.passeditor = InputBox(self.loginscr, 3, size_x - 15, 8 - 1, 12) 
        
        self.connectButton = ButtonBox(self.loginscr, 11, 7, "Connect")
        self.clearButton = ButtonBox(self.loginscr, 11, 27, "Clear")
        self.quitButton = ButtonBox(self.loginscr, 11, 47, "Quit")
        
        self.items = [self.logineditor, self.passeditor, self.connectButton, self.clearButton, self.quitButton]
        
        self.loginscr.keypad(True)
        self.loginscr.refresh()
    
    def start(self):
        """Start interaction loop of the window"""
        curses.nonl()
        
        self.items[0].focusOn()
        index = 0
        
        while True:
            c = self.loginscr.getch()
            
            if c in [curses.KEY_DOWN, curses.ascii.TAB] :
                self.items[index].focusOff()
                index = (index + 1) % len(self.items)
                self.items[index].focusOn()
                
            elif c in [curses.KEY_UP]:
                self.items[index].focusOff()
                index = (index - 1) % len(self.items)
                self.items[index].focusOn()
                
            elif c in [curses.KEY_LEFT]:
                if (self.items[index].isEditable()):
                    pass
                else:
                    curses.ungetch(curses.KEY_UP)
                    
            elif c in [curses.KEY_RIGHT]:
                if (self.items[index].isEditable()):
                    pass
                else:
                    curses.ungetch(curses.KEY_DOWN)
                    
            elif c in [curses.ascii.CR]:
                if (self.items[index].isEditable()):
                    curses.ungetch(curses.KEY_DOWN)
                else:
                    pass
            
            elif c == ord('q'):
                curses.nl()
                self.loginscr.clear()
                self.loginscr.refresh()
                break
                #return self.logineditor.result(), self.passeditor.result()
                
            else:
                self.loginscr.addstr(curses.unctrl(c) + b' ')
        
        return False, False

class ClientUI(Thread, Observer):

    """
    The default client user interface (UI).
    
    Attribut(s):
    - facade: the facade of the domain layer
    #- encoding: the locale encoding
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
        
        #locale.setlocale(locale.LC_ALL, '') # Set locale setting
        #self.encoding = locale.getpreferredencoding() # Get locale encoding
        
        # Main window
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.noecho() 
        try: curses.curs_set(0)
        except: pass
        
        # Menu window
        self.menuscr = curses.newwin(2, curses.COLS, 0, 0)
        self.menuscr.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.menuscr.addstr(0, curses.COLS - len(message) - 1, message)
        self.menuscr.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.menuscr.addch(1, curses.COLS - len(message) - 3 , curses.ACS_BTEE)
    
        self.menuscr.addstr(0, 0, "S", curses.A_UNDERLINE)
        self.menuscr.addstr(0, 1, "earch")
        self.menuscr.addstr(0, 7, "N", curses.A_UNDERLINE)
        self.menuscr.addstr(0, 8, "ew")
        self.menuscr.addstr(0, 11, "D", curses.A_UNDERLINE)
        self.menuscr.addstr(0, 12, "isconnect")
        self.menuscr.addstr(0, 22, "Q", curses.A_UNDERLINE)
        self.menuscr.addstr(0, 23, "uit")
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
        #if (login != False):
            #self.facade.setCredentials(login, passwd)
            #login = passwd = "                            " 

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
        self.statscr.addstr(value + ' ' + str(currenty) + ' ' + str(currentx))
        #self.statscr.addstr(value)
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position


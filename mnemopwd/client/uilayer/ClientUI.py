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
from client.uilayer.uiapplication.MainWindow import MainWindow

"""
Standard curses user interface.
"""

locale.setlocale(locale.LC_ALL, '') # Set locale setting

class ClientUI(Thread, Observer):
    """
    The default client user interface (UI).
    
    Attribut(s):
    - facade: the facade of the domain layer
    - wmain: the main window of the UI
    
    Method(s):
    - stop: stop the interaction loop and close the UI
    - run: start the interaction loop
    - update: update the UI (implementation of the Observer class method)
    """

    encoding = locale.getpreferredencoding() # Get locale encoding

    def __init__(self, facade):
        """Create an initialize UI"""
        Thread.__init__(self)
        Observer.__init__(self)
        
        self.corefacade = facade # Store the facade of the domain layer
        
        # curses initialization
        self.window = curses.initscr()
        self.window.keypad(1) # Let special keys be a single key
        curses.noecho() # No echoing key pressed
        try: curses.curs_set(0) # No cursor
        except: pass
        curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON2_CLICKED | 
                         curses.BUTTON3_CLICKED | curses.BUTTON4_CLICKED) # Mouse events
        
        # Open the main window
        self.wmain = MainWindow(self)

    def stop(self):
        """Stop UI and return to normal interaction"""
        curses.nocbreak()
        self.window.keypad(False)
        try: curses.curs_set(2)
        except: pass
        curses.echo()
        curses.endwin()

    def run(self):
        """The loop interaction"""
        self.wmain.start() # Interaction as long as window is not closed
        self.corefacade.stop() # Stop the core layer

    def update(self, property, value):
        """Implementation of the method of the class Observer."""
        if property == "connection.state":
            self.wmain.update_status(value)
        if property == "connection.state.login":
            self.wmain.update_window(property, value)
        if property == "connection.state.logout":
            self.wmain.update_window(property, value)
        if property == "connection.state.error":
            self.wmain.update_window(property, value)
            
    def inform(self, property, value):
        """Indicate to core layer one user demand"""
        self.corefacade.command(property, value)

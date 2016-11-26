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

from ..util.funcutils import Observer
from .uiapplication.MainWindow import MainWindow

"""
Standard curses user interface.
"""

locale.setlocale(locale.LC_ALL, '')  # Set locale setting


class ClientUI(Thread, Observer):
    """
    The default client user interface (UI).

    Attribute(s):
    - corefacade: the facade of the domain layer
    - wmain: the main window of the UI

    Method(s):
    - stop: stop the interaction loop and close the UI
    - run: start the interaction loop
    - update: update the UI (implementation of the Observer class method)
    """

    encoding = locale.getpreferredencoding()  # Get locale encoding

    def __init__(self, facade):
        """Create an initialize UI"""
        Thread.__init__(self)
        Observer.__init__(self)

        self.corefacade = facade  # Store the facade of the domain layer

        # curses initialization
        self.window = curses.initscr()

        if curses.COLS < 80 or curses.LINES < 24:
            curses.endwin()
            print("Please consider to use at least a 80x24 terminal size.")
            raise Exception()

        self.window.keypad(1)  # Let special keys be a single key
        curses.noecho()  # No echoing key pressed
        curses.nonl()  # Leave newline mode
        try:
            curses.curs_set(0)  # No cursor
        except:
            pass

        # Open the main window
        self.wmain = MainWindow(self)

    def clear_content(self):
        """Clear the window content"""
        self.window.erase()
        self.window.refresh()

    def stop(self):
        """Stop UI and return to normal interaction"""
        try:
            curses.curs_set(2)
        except:
            pass
        curses.nonl()  # Enter newline mode
        curses.nocbreak()
        curses.echo()
        self.window.keypad(False)
        curses.endwin()

    def run(self):
        """The loop interaction"""
        self.wmain.start()  # Interaction as long as window is not closed
        self.corefacade.stop()  # Stop the core layer

    def update(self, key, value):
        """Implementation of the method of the class Observer."""
        if key == "connection.state":
            # Update connection state
            self.wmain.update_status(value)
        if key == "connection.state.login":
            # Login
            self.wmain.update_window(key, value)
        if key == "connection.state.logout":
            # Logout
            self.wmain.update_window(key, value)
        if key == "connection.state.error":
            # An exception occurred
            self.wmain.update_window(key, value)
        if key == "application.state":
            # Update application state
            self.wmain.update_status(value)
        if key == "application.keyhandler":
            # Assign key handler object
            self.wmain.update_window(key, value)
        if key == "application.state.loadbar":
            # Update load bar
            self.wmain.update_load_bar(*value)
        if key == "application.searchblock.result":
            # Signal some results after a research or an exportation
            self.wmain.update_window(key, value)
        if key == "application.searchblock.oneresult":
            # Add one result
            self.wmain.update_window(key, value)
        if key == "application.searchblock.tryoneresult":
            # Try to add one result to a previous research
            self.wmain.update_window(key, value)
        if key == "application.searchblock.updateresult":
            # Update one previous result
            self.wmain.update_window(key, value)
        if key == "application.searchblock.removeresult":
            # Remove one previous result
            self.wmain.update_window(key, value)

    def inform(self, key, value):
        """Indicate to core layer a user demand"""
        self.corefacade.command(key, value)

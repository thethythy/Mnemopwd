# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
import hashlib
import os
import time
import math

from ...util.Configuration import Configuration
from ...util.funcutils import sfill
from ..uicomponents.BaseWindow import BaseWindow
from ..uicomponents.ButtonBox import ButtonBox
from .LoginWindow import LoginWindow
from .UserAccountWindow import UserAccountWindow
from .UserAccountDeletionWindow import UserAccountDeletionWindow
from .UnlockScreenWindow import UnlockScreenWindow
from .EditionWindow import EditionWindow
from .SearchWindow import SearchWindow
from .ApplicationMenu import ApplicationMenu
from .CreateMenu import CreateMenu


class MainWindow(BaseWindow):
    """
    The main window of the client application
    """

    def __init__(self, facade):
        """Create the window"""
        BaseWindow.__init__(self, None, curses.LINES - 2, curses.COLS, 0, 0)
        self.uifacade = facade  # Reference on ui layer facade
        self.connected = False  # Login state
        self.login = None       # User account login
        self.hpassword = None   # User account password

        # Menu zone
        self.applicationButton = ButtonBox(self, 0, 0, "MnemoPwd", shortcut='e')
        self.newButton = ButtonBox(self, 0, 11, "New", shortcut='N')
        self.searchButton = ButtonBox(self, 0, 17, "Search", shortcut='r')

        # Ordered list of shortcut keys
        self.shortcuts = ['e', 'N', 'r']

        # Ordered list of components
        self.items = [self.applicationButton, self.newButton, self.searchButton]

        # Edition window
        self.editscr = EditionWindow(
            self, curses.LINES - 4, int(curses.COLS * 2/3), 2,
            int(curses.COLS * 1/3), "Edition", Configuration.btypes)

        # Search window
        self.searchscr = SearchWindow(
            self, curses.LINES - 4, int(curses.COLS * 1/3), 2, 0, "Search")

        # Status window
        self.statscr = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.statscr.refresh()

        self._decorate()

    def _decorate(self):
        """Show specific content"""
        self.window.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.window.addstr(0, curses.COLS - len(message) - 1, message)
        self.window.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.window.addch(1, curses.COLS - len(message) - 3, curses.ACS_BTEE)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.window.refresh()

    def lock_screen(self):
        """Lock / unlock the screen"""
        if self.connected:
            self.uifacade.clear_content()
            self.window.timeout(-1)
            self.window.addstr(
                int(curses.LINES / 2), int(curses.COLS / 2 - 13),
                "Hit a key to unlock screen")
            self.window.getch()
            while UnlockScreenWindow(self).start() is False:
                self.window.addstr(
                    int(curses.LINES / 2), int(curses.COLS / 2 - 13),
                    "Hit a key to unlock screen")
                self.window.getch()
            self.redraw()

    def hash_password(self, password):
        """Compute a digest of the password. USe a random salt value"""
        ho = hashlib.sha512()
        ho.update(password.encode() + self.salt)
        return ho.digest()

    def _get_credentials(self):
        """Get login/password"""
        self.update_status('Please start a connection')
        login, passwd = LoginWindow(self).start()
        if login is not False:
            self.login = login
            self.salt = (os.urandom(256))[64:128]  # Random salt value
            self.hpassword = self.hash_password(passwd)
            Configuration.first_execution = False
            self.uifacade.inform("connection.open.credentials", (login, passwd))

    def _set_credentials(self):
        """Create a new user account"""
        login, passwd = UserAccountWindow(self).start()
        if login is not False:
            self.login = login
            self.salt = (os.urandom(256))[64:128]  # Random salt value
            self.hpassword = self.hash_password(passwd)
            Configuration.first_execution = True
            self.uifacade.inform("connection.open.credentials", (login, passwd))

    def _delete_user_account(self):
        """Try to delete a user account"""
        result = UserAccountDeletionWindow(self).start()
        if result:
            self.uifacade.inform("connection.close.deletion", None)

    def _handle_block(self, number, idblock):
        """Start block edition"""
        # Change status message
        message = "Edit '" + ((Configuration.btypes[str(number)])["1"])["name"]\
                  + "' information block"
        self.update_status(message)

        # Prepare edition window
        if idblock is None:
            self.editscr.set_type(number)

        # Do edition
        try:
            result, sib = self.editscr.start()
        except:
            self.update_status('Edition impossible: a string is too long (close then resize window).')
            return

        # According to the result, save / update or delete or do nothing
        if result is True:
            self.uifacade.inform("application.editblock", (idblock, sib))
        elif sib is True:
            self.uifacade.inform("application.deleteblock", idblock)
        else:
            self.update_status('')

    def _search_block(self):
        """Start searching block"""
        self.searchscr.pre_search()
        return self.searchscr.start()

    def start(self, timeout=-1):
        """See mother class"""
        if Configuration.first_execution:
            # Propose to create a user account
            self._set_credentials()
        else:
            # Propose to connect to an existing user account
            self._get_credentials()

        # Automatic lock screen
        counter = 0
        timer = Configuration.lock * 60 * 1000  # Timer in ms

        while True:
            # Interaction loop
            result = BaseWindow.start(self, timeout=100)  # Timeout of 100 ms

            # Lock screen ?
            if result == 'timeout' and timer > 0 and self.connected:
                counter += 100
                if counter >= timer:
                    self.lock_screen()
                    counter = 0
            else:
                counter = 0

            # Main menu
            if result == self.applicationButton:
                self.applicationButton.focus_off()
                result = ApplicationMenu(self, 1, 0, self.connected).start()
                if result == ApplicationMenu.ITEM1:  # Login/logout
                    if not self.connected:
                        self._get_credentials()  # Try a connection
                    else:
                        # Disconnection
                        self.uifacade.inform("connection.close", None)
                if result == ApplicationMenu.ITEM2:  # Create user account
                    if not self.connected:
                        # Try to create a new user account
                        self._set_credentials()
                    else:
                        self.update_status('You must be disconnected to create a new user account')
                if result == ApplicationMenu.ITEM3:  # Delete user account
                    if self.connected:
                        # Try to delete user account
                        self._delete_user_account()
                    else:
                        self.update_status('You must be connected to a user account to delete it')
                if result == ApplicationMenu.ITEM4:  # Lock screen
                    if self.connected:
                        self.lock_screen()
                if result == ApplicationMenu.ITEM5:  # Quit application
                    if self.connected:
                        # Disconnection
                        self.uifacade.inform("connection.close", None)
                        time.sleep(0.1)  # Waiting for task execution
                    break

            # Create a new entry
            elif result == self.newButton:
                if self.connected:
                    self.newButton.focus_off()
                    result = CreateMenu(self, Configuration.btypes, 1, 11).start()
                    if result:
                        self._handle_block(result, None)
                else:
                    self.update_status('Please start a connection')

            # Search some entries
            elif result == self.searchButton:
                if self.connected:
                    self.searchButton.focus_off()
                    number_type, idblock = self._search_block()
                    if type(number_type) is int:
                        self._handle_block(number_type, idblock)
                else:
                    self.update_status('Please start a connection')

    def _post_close(self, value):
        """Actions to do after the connection has been closed"""
        self.login = self.hpassword = None
        self.connected = False
        self.update_status(value)
        self.editscr.clear_content()
        self.searchscr.clear_content()

    def update_window(self, key, value):
        """Update the main window content"""
        if key == "connection.state.login":
            # Normal login
            self.connected = True
            self.update_status(value)
        if key == "connection.state.logout":
            # Normal logout
            self._post_close(value)
        if key == "connection.state.error":
            # Exception
            self._post_close(value)
            curses.flash()
        if key == "application.keyhandler":
            # KeyHandler object assignation
            self.editscr.set_keyhandler(value)
        if key == "application.searchblock.result":
            # Search or importation result
            self.searchscr.post_search(value)
        if key == "application.searchblock.oneresult":
            # Add one result
            self.searchscr.add_a_result(*value)
        if key == "application.searchblock.tryoneresult":
            # Try to add a new block to panel result
            self.searchscr.try_add_a_result(*value)
        if key == "application.searchblock.updateresult":
            # Update one result
            self.searchscr.update_a_result(*value)
        if key == "application.searchblock.removeresult":
            # Remove one result
            self.searchscr.remove_a_result(value)
        if key == "application.editionblock.seteditors":
            # Set edition window
            number_type, sib = value
            self.editscr.set_type(number_type)
            self.editscr.set_infos(number_type, sib)
        if key == "application.editionblock.cleareditors":
            # Clear edition window
            self.editscr.clear_content()

    def update_load_bar(self, actual, maxi):
        max_len = curses.COLS - 20
        actual_len = int(actual * max_len / maxi)
        percent = str(math.floor(actual_len * 100 / max_len))
        message = sfill(actual_len, '█')
        currenty, currentx = curses.getsyx()  # Save current cursor position
        self.statscr.move(1, 7)
        self.statscr.clrtoeol()  # Clear line
        # Show percentage then load bar
        self.statscr.addstr(1, 8, percent + "%" + " [" + str(actual) + "]")
        self.statscr.addstr(1, 19, message)
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)  # Restore cursor position

    def update_status(self, value):
        """Update the status window content"""
        currenty, currentx = curses.getsyx()
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
        curses.setsyx(currenty, currentx)

    def redraw(self):
        """See mother class"""
        self._decorate()
        self.editscr.redraw()
        self.searchscr.redraw()
        self.update_status('')
        BaseWindow.redraw(self)

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

from ...util.Configuration import Configuration
from ..uicomponents.TitledBorderWindow import TitledBorderWindow
from ..uicomponents.LabelBox import LabelBox
from ..uicomponents.InputBox import InputBox
from ..uicomponents.ButtonBox import ButtonBox


class UserAccountDeletionWindow(TitledBorderWindow):
    """
    A window to confirm user account deletion
    """

    def __init__(self, parent):
        """Create the window"""
        size_y = 14
        size_x = 60

        TitledBorderWindow.__init__(self, parent, size_y, size_x,
                                    int(curses.LINES / 2) - int(size_y / 2),
                                    int(curses.COLS / 2) - int(size_x / 2),
                                    "User account deletion confirmation window",
                                    modal=True, colourT=Configuration.colourT,
                                    colourD=Configuration.colourD)

        LabelBox(self, 5, 2, "Login", colour=Configuration.colourD)
        LabelBox(self, 8, 2, "Password", colour=Configuration.colourD)

        # Ordered list of shortcut keys
        self.shortcuts = ['', '', 'e', 'l', 'a']

        # Editable components
        self.logineditor = InputBox(self, 3, size_x - 15, 5 - 1, 12,
                                    self.shortcuts,
                                    colourD=Configuration.colourD)
        self.passeditor = InputBox(self, 3, size_x - 15, 8 - 1, 12,
                                   self.shortcuts, secret=True,
                                   colourD=Configuration.colourD)

        # Actionable components
        posx = gap = int(((size_x - 2) - (9 + 7 + 8)) / 4) + 1
        self.deleteButton = ButtonBox(self, 11, posx, "Delete", 'e',
                                      colour=Configuration.colourB)
        posx = posx + 9 + gap
        self.clearButton = ButtonBox(self, 11, posx, "Clear", 'l',
                                     colour=Configuration.colourB)
        posx = posx + 7 + gap
        self.cancelButton = ButtonBox(self, 11, posx, "Cancel", 'a',
                                      colour=Configuration.colourB)

        # Ordered list of components
        self.items = [self.logineditor, self.passeditor, self.deleteButton,
                      self.clearButton, self.cancelButton]

        self.window.refresh()

    def _control_conditions(self):
        """Control conditions for deleting user account"""
        if self.logineditor.value is None:
            self.index = 0
            self.parent.update_status("Wrong login")
            return False
        if self.passeditor.value is None:
            self.index = 1
            self.parent.update_status("Wrong password")
            return False
        if self.logineditor.value == self.parent.login and \
           self.parent.hash_password(self.passeditor.value) == self.parent.hpassword:
            return True
        else:
            self.index = 0
            self.parent.update_status("Wrong login or password")
            return False

    def start(self, timeout=-1):
        """See mother class"""
        while True:
            result = TitledBorderWindow.start(self)  # Default controller

            # Next item for editable items
            if type(result) is InputBox:
                result.focus_off()
                self.index = (self.index + 1) % len(self.items)

            # Cancel login window
            elif result is False or result == self.cancelButton:
                self.close()
                return False

            # Clear all input boxes
            elif result == self.clearButton:
                self.logineditor.clear()
                self.passeditor.clear()
                self.clearButton.focus_off()
                self.index = 0

            # Try to return login and password
            elif result == self.deleteButton:
                self.deleteButton.focus_off()
                if self._control_conditions():
                    self.parent.update_status("")
                    self.close()
                    return True

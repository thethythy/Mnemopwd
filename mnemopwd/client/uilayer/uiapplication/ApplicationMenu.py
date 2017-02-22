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

from ..uicomponents.BaseWindow import BaseWindow
from ..uicomponents.MetaButtonBox import MetaButtonBox
from ...util.funcutils import sfill


class ApplicationMenu(BaseWindow):
    """
    The menu for login/logout, user account, quit application
    """

    ITEM1 = 'LOGINOUT'
    ITEM2 = 'CUACCOUNT'
    ITEM3 = 'DUACCOUNT'
    ITEM4 = 'LOCK'
    ITEM5 = 'QUIT'

    def __init__(self, parent, y, x, connected):
        """Create the menu"""
        # Create the window
        BaseWindow.__init__(self, parent, 7, 19 + 5, y, x, menu=True, modal=True)
        self.window.border()
        self.window.refresh()

        # Login/logout button
        if connected:
            name = 'Logout' + sfill(19 - 6, ' ')
        else:
            name = 'Login' + sfill(19 - 5, ' ')
        self.items.append(MetaButtonBox(
            self, 1, 1, name, shortcut='L', data=self.ITEM1))

        # Create user account button
        self.items.append(MetaButtonBox(
            self, 2, 1, 'Create user account', shortcut='n', data=self.ITEM2))

        # Delete user account button
        self.items.append(MetaButtonBox(
            self, 3, 1, 'Delete user account', shortcut='e', data=self.ITEM3))

        # Lock screen
        name = 'Lock screen' + sfill(19 - 11, ' ')
        self.items.append(MetaButtonBox(
            self, 4, 1, name, shortcut='k', data=self.ITEM4))

        # Quit button
        name = 'Quit' + sfill(19 - 4, ' ')
        self.items.append(MetaButtonBox(
            self, 5, 1, name, shortcut='u', data=self.ITEM5))

        # Ordered list of shortcut keys
        self.shortcuts = ['L', 'n', 'e', 'k', 'u']

    def start(self, timeout=-1):
        """See mother class"""
        while True:
            # Interaction loop
            result = BaseWindow.start(self)

            # Escape
            if result is False or type(result) is int:
                self.close()
                return False

            # Return the number
            else:
                self.close()
                return self.items[self.index].get_data()

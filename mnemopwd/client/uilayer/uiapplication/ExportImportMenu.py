# -*- coding: utf-8 -*-

# Copyright (c) 2017, Thierry Lemeunier <thierry at lemeunier dot net>
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

from ..uicomponents.BaseWindow import BaseWindow
from ..uicomponents.MetaButtonBox import MetaButtonBox
from ...util.Configuration import Configuration


class ExportImportMenu(BaseWindow):
    """
    The menu for exporting and importing
    """

    ITEM1 = 'CLEAR_EXPORT'
    ITEM2 = 'CRYPT_EXPORT'
    ITEM3 = 'CLEAR_IMPORT'
    ITEM4 = 'CRYPT_IMPORT'

    def __init__(self, parent, y, x):
        """Create the menu"""

        # Create the window
        BaseWindow.__init__(self, parent, 7, 23 + 5, y, x, menu=True, modal=True)

        # Border and horizontal line
        self.window.attrset(Configuration.colourD)
        self.window.border()
        self.window.hline(3, 1, curses.ACS_BULLET, 23 + 3)
        self.window.refresh()
        self.window.attrset(0)

        # Exportation in clear text
        name = 'Clear text exportation '
        self.items.append(MetaButtonBox(self, 1, 1, name, shortcut='l',
                                        data=self.ITEM1,
                                        colour=Configuration.colourB))

        # Exportation in cypher text
        name = 'Cypher text exportation'
        self.items.append(MetaButtonBox(self, 2, 1, name, shortcut='p',
                                        data=self.ITEM2,
                                        colour=Configuration.colourB))

        # Importation from clear text
        name = 'Clear text importation '
        self.items.append(MetaButtonBox(self, 4, 1, name, shortcut='i',
                                        data=self.ITEM3,
                                        colour=Configuration.colourB))

        # Importation from cypher text
        name = 'Cypher text importation'
        self.items.append(MetaButtonBox(self, 5, 1, name, shortcut='m',
                                        data=self.ITEM4,
                                        colour=Configuration.colourB))

        # Ordered list of shortcut keys
        self.shortcuts = ['l', 'p', 'I', 'm']

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

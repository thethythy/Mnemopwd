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

from ..uicomponents.BaseWindow import BaseWindow
from ..uicomponents.MetaButtonBox import MetaButtonBox
from ...util.Configuration import Configuration
from ...util.funcutils import sfill


class CreateMenu(BaseWindow):
    """
    The menu for creating a new entry in the database
    """

    def __init__(self, parent, btypes, y, x):
        """Create the menu according to block types"""

        # Create the window
        max_len = 0
        for btype in btypes.values():
            max_len = max(max_len, len((btype["1"])["name"]))
        BaseWindow.__init__(self, parent, len(btypes) + 2, max_len + 5, y, x,
                            menu=True, modal=True)
        self.window.attrset(Configuration.colourD)
        self.window.border()
        self.window.refresh()
        self.window.attrset(0)

        # Add buttons (preserving the order indicated in the json file)
        posy = 1
        for i in range(1, len(btypes) + 1):
            btype = btypes[str(i)]
            name = btype["1"]["name"]
            high = (len(btype) - 1) * 4 + 2
            if high <= (curses.LINES - 4):
                self.items.append(
                    MetaButtonBox(self, posy, 1,
                                  name + sfill(max_len - len(name), ' '),
                                  data=i, colour=Configuration.colourB))
                posy += 1
            else:
                self.parent.update_status(
                    "The type '{}' has too many fields for the actual window size".format(name))

    def start(self, timeout=-1):
        """See mother class"""
        while True:
            # Interaction loop
            result = BaseWindow.start(self)

            # Escape
            if result is False or type(result) is int:
                self.close()
                return False

            # Return the number of block type selected
            else:
                self.close()
                return self.items[self.index].get_data()

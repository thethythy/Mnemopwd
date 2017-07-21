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

import re
import curses
import curses.ascii

from ...util.Configuration import Configuration
from ..uicomponents.TitledOnBorderWindow import TitledOnBorderWindow
from ..uicomponents.Component import Component
from ..uicomponents.InputBox import InputBox
from ..uicomponents.ListBox import ListBox


class SearchWindow(TitledOnBorderWindow):
    """
    The search window: a window for searching blocks
    """

    def __init__(self, parent, h, w, y, x, title):
        """Create the window"""

        TitledOnBorderWindow.__init__(self, parent, h, w, y, x, title,
                                      modal=True, menu=True,
                                      colourT=Configuration.colourT,
                                      colourD=Configuration.colourD)

        # Pattern editor
        self.patternEditor = InputBox(self, 3, w - 4, 1, 2, show=False,
                                      colourD=Configuration.colourD)

        # Result panel
        self.resultPanel = ListBox(self, h - 3 - 2, w - 4, 4, 2)
        self.resultPanel.set_listener(self)
        self.nbResult = self.nbMaxResult = 0

        self.shortcuts = []
        self.items = [self.patternEditor, self.resultPanel]

        self.window.refresh()

    def lock_screen(self):
        """Lock the screen"""
        self.parent.lock_screen()

    def clear_content(self):
        """Clear the window content"""
        self.nbResult = self.nbMaxResult = 0
        self.resultPanel.clear_content()
        self.patternEditor.clear()
        self.patternEditor.hide()

    def update_status(self, message):
        """Update parent status"""
        self.parent.update_status(message)

    def update(self, item):
        """
        Update window according the item selected in the ListBox.
        This method is called by the ListBox widget instance.
        """
        if isinstance(item, Component) and item.has_focus():
            idblock, sib = item.get_data()
            atuple = int(sib['info1'].decode()), sib
            self.parent.update_window(
                "application.editionblock.seteditors", atuple)
        else:
            self.parent.update_window(
                "application.editionblock.cleareditors", None)

    def pre_search(self):
        """Prepare window before searching"""
        self.update_status("Edit pattern filter")
        self.patternEditor.show()

    def do_search(self):
        """Start a searching operation"""
        if self.patternEditor.value is not None:
            self.nbResult = self.nbMaxResult = 0
            self.resultPanel.clear_content()
            pattern = self.patternEditor.value
            if self._is_pattern_all(pattern):
                self.parent.uifacade.inform("application.exportblock", None)
            else:
                self.parent.uifacade.inform("application.searchblock", pattern)

    def post_search(self, table_result):
        """Prepare window after searching"""
        # Set the number of blocks found
        self.nbResult = 0
        self.nbMaxResult = len(table_result)
        # Populate result panel
        for index in table_result:
            self.parent.uifacade.inform(
                "application.searchblock.blockvalues", index)

    def add_a_result(self, idblock, sib):
        """Add a search result in the panel"""

        self.nbResult += 1
        the_end = self.nbResult >= self.nbMaxResult  # All results treated ?

        # Create and add a button to the result panel
        label = sib['info2'].decode()[:self.w - 4 - 1 - 2]
        self.resultPanel.add_item(label, idblock, data=sib, scroll=the_end)

        # Change focus on result panel if it was the last result
        if the_end and self.index == 0:
            self.items[self.index].focus_off()
            self.index += 1  # Next item: the result panel

    def try_add_a_result(self, idblock, sib):
        """Try to add a new block in the result panel"""
        if self.patternEditor.value is not None:
            pattern = self.patternEditor.value
            if self._is_pattern_all(pattern):
                self.patternEditor.show()
                self.add_a_result(idblock, sib)
            else:
                for j in range(1, sib.nbInfo + 1):  # For all info in sib
                    try:
                        if re.search(pattern.upper(),
                                     sib['info' + str(j)].decode().upper()) \
                                is not None:
                            self.patternEditor.show()
                            self.add_a_result(idblock, sib)
                            break  # One info match so stop loop now
                    except KeyError:
                        continue

    def update_a_result(self, idblock, sib):
        """Update a previous search result"""
        self.resultPanel.update_item(idblock, sib)

    def remove_a_result(self, idblock):
        """Remove a previous search result"""
        self.resultPanel.remove_item(idblock)

    def start(self, timeout=-1):
        """See mother class"""

        # Automatic lock screen
        counter = 0
        timer = Configuration.lock * 60 * 1000  # Timer in ms

        while True:
            # Start default controller (timeout of 100 ms)
            result = TitledOnBorderWindow.start(self, 100)

            # Lock screen ?
            if result == 'timeout' and timer > 0:
                counter += 100
                if counter >= timer:
                    self.parent.lock_screen()
                    counter = 0
            else:
                counter = 0

            # Try to create or update the block
            if result == self.patternEditor:
                self.do_search()

            # Navigate in result panel
            elif result == self.resultPanel:
                self.update_status("Navigate or hit return to edit")
                result = self.resultPanel.start(timeout=100)
                self.update_status("")
                if result == -1:
                    self.index -= 1  # Focus on previous item
                elif result == 1 or result is False:
                    self.index -= 1  # Focus on next item
                    curses.ungetch(curses.ascii.ESC)  # Quit window
                elif isinstance(result, Component):
                    idblock, sib = result.get_data()
                    # Return number_type, idblock
                    return int(sib['info1'].decode()), idblock

            # Quit window or Escape
            elif result == 1 or result == -1 or result is False:
                self.index = 0  # For focusing on first item at the return
                self.update_status("")  # Clear status bar
                if self.nbResult == 0:
                    self.clear_content()  # Hide contents if there is no result

                return False, False

    def _is_pattern_all(self, pattern):
        """Test if the pattern corresponds to '*'"""
        return pattern == '*' or pattern in ['ALL']

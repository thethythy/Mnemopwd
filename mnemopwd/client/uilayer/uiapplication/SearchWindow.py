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

import curses
import curses.ascii

from client.uilayer.uicomponents.TitledOnBorderWindow import TitledOnBorderWindow
from client.uilayer.uicomponents.Component import Component
from client.uilayer.uicomponents.InputBox import InputBox
from client.uilayer.uiapplication.SearchResultPanel import SearchResultPanel


class SearchWindow(TitledOnBorderWindow):
    """
    The search window: a window for searching blocks
    """

    def __init__(self, parent, h, w, y, x, title):
        """Create the window"""
        TitledOnBorderWindow.__init__(self, parent, h, w, y, x, title, modal=True, menu=True)

        # Pattern editor
        self.patternEditor = InputBox(self, 3, w - 4, 1, 2, show=False)

        # Result panel
        self.resultPanel = SearchResultPanel(self, h - 3 - 2, w - 4, 4, 2, modal=True, menu=True)
        self.nbResult = self.nbMaxResult = 0

        self.shortcuts = []
        self.items = [self.patternEditor, self.resultPanel]

        self.window.refresh()

    def clear_content(self):
        """Clear the window content"""
        self._clear_result_panel()
        self.patternEditor.clear()
        self.patternEditor.hide()

    def _clear_result_panel(self):
        """Clear the content of the result panel"""
        self.nbResult = self.nbMaxResult = 0
        for item in self.resultPanel.items.copy():
            self.resultPanel.remove_item(item)

    def _do_search(self, pattern):
        """Do searching operation on server side"""
        if pattern == '*' or pattern in ['ALL', 'All', 'all']:
            self.parent.uifacade.inform("application.exportblock", None)
        else:
            self.parent.uifacade.inform("application.searchblock", pattern)

    def update_status(self, message):
        """Update parent status"""
        self.parent.update_status(message)

    def update_window(self, key, value):
        self.parent.update_window(key, value)

    def pre_search(self):
        """Prepare window before searching"""
        self.patternEditor.show()

    def do_search(self):
        """Start a searching operation"""
        if self.patternEditor.value is not None:
            self._clear_result_panel()
            self._do_search(self.patternEditor.value)

    def post_search(self, table_result):
        """Prepare window after searching"""
        # Set the number of blocks found
        self.nbMaxResult = len(table_result)
        # Populate result panel
        for index in table_result:
            self.parent.uifacade.inform("application.searchblock.blockvalues", index)

    def add_a_result(self, index, values):
        """Add a search result in the panel"""
        # Create and add a button to the result panel
        self.nbResult += 1
        self.resultPanel.add_item(index, values)
        # Change focus on result panel if it is the last result
        if self.nbResult == self.nbMaxResult and self.index == 0:
            self.focus_off_force(1)

    def focus_off_force(self, direction):
        """This window must lost focus"""
        self.items[self.index].focus_off()
        self.index += direction
        curses.ungetch(curses.ascii.CR)

    def start(self, timeout=-1):
        """See mother class"""
        while True:
            self.update_status("Edit pattern filter")
            result = TitledOnBorderWindow.start(self, 100)  # Default controller (timeout of 100 ms)

            # Try to create or update the block
            if result == self.patternEditor:
                self.do_search()

            # Navigate in result panel
            elif result == self.resultPanel:
                self.update_status("Navigate or hit return to edit")
                result = self.resultPanel.start()
                self.update_status("")
                if result == -1:
                    self.index -= 1  # Focus on previous item
                elif result == 1 or result is False:
                    self.index -= 1  # Focus on next item
                    curses.ungetch(curses.ascii.ESC)  # Quit window
                elif isinstance(result, Component):
                    return result.get_data()  # Return idBlock, block values

            # Quit window or Escape
            elif result == 1 or result == -1 or result is False:
                self.index = 0  # For focusing on first item at the return
                self.update_status("")  # Clear status bar
                if self.nbResult == 0:
                    self.patternEditor.hide()  # Hide pattern editor if there is no result
                return False, False

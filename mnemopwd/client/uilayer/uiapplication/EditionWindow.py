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

from client.uilayer.uicomponents.TitledOnBorderWindow import TitledOnBorderWindow
from client.uilayer.uicomponents.ButtonBox import ButtonBox
from client.uilayer.uicomponents.InputBox import InputBox
from client.util.funcutils import sfill

class EditionWindow(TitledOnBorderWindow):
    """
    The edition window: a window for block edition
    """

    def __init__(self, parent, h, w, y, x, title, btypes):
        """Create the window"""
        TitledOnBorderWindow.__init__(self, parent, h, w, y, x, title)

        # Buttons
        posy = h - 2
        posx = gap = int(((w - 2) - (6 + 7 + 8 + 8)) / 5) + 1
        self.saveButton = ButtonBox(self, posy, posx, "Save", 'A')
        posx = posx + 6 + gap
        self.clearButton = ButtonBox(self, posy, posx, "Clear", 'L')
        posx = posx + 7 + gap
        self.cancelButton = ButtonBox(self, posy, posx, "Cancel", 'N')
        posx = posx + 8 + gap
        self.deleteButton = ButtonBox(self, posy, posx, "Delete", 'T')

        self._shortcuts = ['A', 'L', 'N', 'T']
        self._items = [self.saveButton, self.clearButton, self.cancelButton, self.deleteButton]

        # Separator
        self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
        self.window.refresh()

        # Prepare "panels" for block types
        self.number_type = 0
        self.cpb = {}
        for i in range(1, len(btypes)+1):
            btype = btypes[str(i)]

            # Search label max size and get shortcuts list
            shortcuts =[]
            max_len = 0
            for key, infos in btype.items():
                if int(key) > 1 :
                    max_len = max(max_len, len(infos["name"]))
                    shortcuts.append('')
            shortcuts.extend(self._shortcuts)

            # Prepare components for the block type
            infos_comp = {}
            label_posy = 2
            for k in range(1, len(btype)+1):
                info = btype[str(k)]
                info_comp = {}

                # Type name
                if k == 1:
                    info_comp["l_pos_y"] = label_posy
                    info_comp["l_name"] = "Type" + sfill(max_len - 4)
                    info_comp["c_pos_y"] = label_posy
                    info_comp["c_pos_x"] = 2 + max_len + 1
                    info_comp["c_object"] = info["name"]

                # Other field
                else:
                    info_comp["l_pos_y"] = label_posy
                    info_comp["l_name"] = info["name"] + sfill(max_len - len(info["name"]))
                    optional = False
                    if info["option"] == "True": optional = True
                    info_comp["c_object"] = InputBox(self, 3, self.w - 5 - max_len,
                                                     label_posy - 1, 2 + max_len + 1,
                                                     shortcuts, show=False, option=optional)

                label_posy += 3
                infos_comp[k] = info_comp # Add with others components

            self.cpb[i] = infos_comp # Store "the panel" block type

    def setType(self, number):
        """Modify window according the block type selected"""
        if number == self.number_type:
            # Clear all editors
            for item in self.items:
                if item.isEditable(): item.clear()
            self.index = 0
        else:
            # Hide actual components
            self.clear_content()

            # Show components of the selected type
            self.number_type = number
            infos_comp = self.cpb[number]
            items = []
            for i in range(1, len(infos_comp)+1):
                info_comp = infos_comp[i]
                # Show label
                self.window.addstr(info_comp["l_pos_y"], 2, info_comp["l_name"])
                # Show component
                if i == 1:
                    self.window.addstr(info_comp["c_pos_y"], info_comp["c_pos_x"], info_comp["c_object"])
                else:
                    info_comp["c_object"].show()
                    items.append(info_comp["c_object"])

            self.window.refresh()
            # Construction of shortcuts and items lists
            self.shortcuts = info_comp["c_object"].shortcuts
            items.extend(self._items)
            self.items = items

    def clear_content(self):
        """Clear the window content"""
        if self.number_type > 0:
            infos_comp = self.cpb[self.number_type]
            for i in range(1, len(infos_comp)+1):
                info_comp = infos_comp[i]
                self.window.addstr(info_comp["l_pos_y"], 2, sfill(self.w - 3))
                if i > 1: info_comp["c_object"].hide()
            self.window.refresh()
            self.shortcuts = self.items = []
            self.number_type = self.index = 0

    def start(self):
        """See mother class"""
        while True:
            result = TitledOnBorderWindow.start(self) # Default controller

            # Try to create or update the block
            if result == self.saveButton:
                self.saveButton.focusOff()
                complete = True
                values = []
                values.append(str(self.number_type)) # Add number_type for restoring purpose
                for index, item in enumerate(self.items):
                    if item.isEditable() :
                        if not item.option and item.value is None :
                            self.index = index
                            complete = False
                            break
                        if item.value is not None:
                            values.append(item.value) # Add expected and optional values
                if complete:
                    self.clear_content()
                    return True, values

            # Clear all input boxes
            elif result == self.clearButton:
                for item in self.items:
                    if item.isEditable(): item.clear()
                self.clearButton.focusOff()
                self.index = 0

            # Cancel edition window
            elif result == False or result == self.cancelButton:
                self.cancelButton.focusOff()
                for item in self.items:
                    if item.isEditable(): item.clear()
                self.clear_content()
                return False, False

            # Try to delete the block
            elif result == self.deleteButton:
                pass


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
from ..uicomponents.TitledOnBorderWindow import TitledOnBorderWindow
from ..uicomponents.LabelBox import LabelBox
from ..uicomponents.ButtonBox import ButtonBox
from ..uicomponents.InputBox import InputBox
from ...util.funcutils import sfill
from ....common.SecretInfoBlock import SecretInfoBlock


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
        self.saveButton = ButtonBox(self, posy, posx, "Save", 'S')
        posx = posx + 6 + gap
        self.clearButton = ButtonBox(self, posy, posx, "Clear", 'l')
        posx = posx + 7 + gap
        self.cancelButton = ButtonBox(self, posy, posx, "Cancel", 'a')
        posx = posx + 8 + gap
        self.deleteButton = ButtonBox(self, posy, posx, "Delete", 'e')

        self._shortcuts = ['S', 'l', 'a', 'e']
        self._items = self.items = [self.saveButton, self.clearButton,
                                    self.cancelButton, self.deleteButton]

        # Separator
        self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
        self.window.refresh()

        # Prepare "panels" for block types
        self.new_block = True  # Flag to indicate it is a new block or not
        self.number_type = 0
        self.cpb = {}
        for i in range(1, len(btypes)+1):
            btype = btypes[str(i)]

            # Control size of the screen with the number of fields
            high = (len(btype) - 1) * 4 + 2
            if high > (curses.LINES - 4):
                continue

            # Search label max size and get shortcuts list
            shortcuts = []
            max_len = len("Type")  # This label exists always
            for key, infos in btype.items():
                if int(key) > 1:
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
                    # Label
                    label = "Type" + sfill(max_len - 4, ' ')
                    info_comp["l_object"] = LabelBox(self, label_posy, 2,
                                                     label, show=False)

                    # Label
                    info_comp["c_object"] = LabelBox(self, label_posy,
                                                     2 + max_len + 1,
                                                     info["name"], show=False)

                # Other field
                else:
                    # Label
                    label = info["name"] + sfill(max_len - len(info["name"]), ' ')
                    info_comp["l_object"] = LabelBox(self, label_posy, 2, label,
                                                     show=False)
                    # Editor
                    optional = False
                    if info["option"] == "True":
                        optional = True
                    info_comp["c_object"] = InputBox(
                        self, 3, self.w - 5 - max_len, label_posy - 1,
                        2 + max_len + 1, shortcuts, show=False, option=optional)

                label_posy += 3
                infos_comp[k] = info_comp  # Add with others components

            self.cpb[i] = infos_comp  # Store "the panel" block type

    def set_keyhandler(self, value):
        self.keyH = value

    def set_type(self, number):
        """Modify window according to the block type selected"""
        self.new_block = True  # Flag to indicate it is a new block
        if number == self.number_type:
            # Clear all editors
            self._clear_editors()
            self.index = 0
        else:
            # Hide actual components
            self.clear_content()

            # Show components of the selected type
            self.number_type = number
            infos_comp = self.cpb[number]
            items = []
            for i in range(1, len(infos_comp) + 1):
                info_comp = infos_comp[i]
                # Show label
                info_comp["l_object"].show()
                items.append(info_comp["l_object"])
                # Show component
                info_comp["c_object"].show()
                items.append(info_comp["c_object"])
            self.window.refresh()

            # Construction of shortcuts and items lists
            self.shortcuts = info_comp["c_object"].shortcuts
            items.extend(self._items)
            self.items = items

    def set_infos(self, number_type, sib):
        """Set each information in each editor"""
        self.new_block = False  # Flag to indicate it is an existing block
        # Populate editors
        infos_comp = self.cpb[number_type]
        for i in range(2, len(infos_comp) + 1):
            info_comp = infos_comp[i]
            try:
                info_comp["c_object"].value = sib['info' + str(3 + i - 2)].decode()
                info_comp["c_object"].show()
            except KeyError:
                continue  # Nothing to do because of optional values

    def clear_content(self):
        """Clear the window content"""
        if self.number_type > 0:
            infos_comp = self.cpb[self.number_type]
            for i in range(1, len(infos_comp) + 1):
                info_comp = infos_comp[i]
                info_comp["l_object"].hide()
                if i > 1:
                    info_comp["c_object"].clear()
                info_comp["c_object"].hide()
            self.window.refresh()
            self.shortcuts = []
            self.items = self._items
            self.number_type = self.index = 0

    def _clear_editors(self):
        """Clear all editors"""
        for item in self.items:
            if item.is_editable():
                item.clear()

    def _try_create_sib(self):
        """Try to create or update an information block"""
        complete = True
        sib = SecretInfoBlock(self.keyH)
        # Add number_type for restoring purpose
        sib['info1'] = (str(self.number_type)).encode()
        # Add the block type name
        sib.nbInfo += 1
        sib['info2'] = self.cpb[self.number_type][1]["c_object"].label
        for index, item in enumerate(self.items):
            if item.is_editable():
                if not item.option and item.value is None:
                    self.index = index
                    complete = False
                    sib = None
                    break
                if item.value is not None:
                    sib.nbInfo += 1
                    sib['info' + str(sib.nbInfo)] = item.value.encode()
        return complete, sib

    def start(self, timeout=-1):
        """See mother class"""

        # Automatic lock screen
        counter = 0
        timer = Configuration.lock * 60 * 1000  # Timer in ms

        # Set first widget to be editable
        self.index = 3

        while True:
            # Start default controller
            result = TitledOnBorderWindow.start(self, timeout=100)

            # Lock screen ?
            if result == 'timeout' and timer > 0:
                counter += 100
                if counter >= timer:
                    self.parent.lock_screen()
                    counter = 0
            else:
                counter = 0

            # Next item for editable items
            if type(result) is InputBox:
                result.focus_off()
                self.index = (self.index + 1) % len(self.items)
                if type(self.items[self.index]) is LabelBox:
                    self.index += 1

            # Try to create or update the block
            elif result == self.saveButton:
                self.saveButton.focus_off()
                complete, sib = self._try_create_sib()
                if complete:
                    self._clear_editors()
                    self.clear_content()
                    return True, sib

            # Clear all input boxes
            elif result == self.clearButton:
                self.clearButton.focus_off()
                self._clear_editors()
                self.index = 0

            # Cancel edition window
            elif result is False or result == self.cancelButton:
                self.cancelButton.focus_off()
                self._clear_editors()
                self.clear_content()
                return False, False

            # Try to delete the block
            elif result == self.deleteButton:
                if self.new_block is False:
                    self.deleteButton.focus_off()
                    self._clear_editors()
                    self.clear_content()
                    return False, True

    def redraw(self):
        """See mother class"""
        self.window.hline(self.h - 3, 1, curses.ACS_HLINE, self.w - 2)
        TitledOnBorderWindow.redraw(self)

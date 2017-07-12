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
from pathlib import Path
import os
import stat

from .TitledBorderWindow import TitledBorderWindow
from .Component import Component
from .LabelBox import LabelBox
from .ListBox import ListBox
from .ButtonBox import ButtonBox
from .InputBox import InputBox


class FileChooserWindow(TitledBorderWindow):
    """
    A window for choosing a file name.
    """

    SELECT = 1     # Mode of file selection
    CREATE = 2     # Mode of file creation
    OVERWRITE = 3  # Mode of file overwriting

    def __init__(self, parent, directory, mode=SELECT,
                 colourB=False, colourT=False, colourD=False):
        """Creation of the window"""

        self.directory = directory  # Initial directory
        # Execution mode of the file chooser window
        if mode in [self.SELECT, self.CREATE, self.OVERWRITE]:
            self.mode = mode
        else:
            self.mode = self.SELECT

        # Window centered + title + shadows
        h = curses.LINES - 5
        w = curses.COLS - 10
        y = int(curses.LINES / 2) - int(h / 2)
        x = int(curses.COLS / 2) - int(w / 2)
        TitledBorderWindow.__init__(self, parent, h, w, y, x, "File chooser",
                                    modal=True, colourT=colourT,
                                    colourD=colourD)

        # Directory name
        LabelBox(self, 3, 2, 'Directory:', colour=colourD)
        self.dnameLabel = LabelBox(self, 3, 13,
                                   self._format_name(directory, w - 15),
                                   colour=colourD)

        # Directory content
        self.dirListBox = ListBox(self, h - 12, w - 3, 5, 2, colourD=colourD,
                                  colourB=colourB)
        self.dirListBox.set_listener(self)
        self._populate(directory)

        # Filename editor
        posy = h - 5
        LabelBox(self, posy, 2, 'File name:')
        self.fnameInput = InputBox(self, 3, w - 5 - 10, posy - 1, 10 + 3,
                                   colourD=colourD)

        # Separator
        self.window.attrset(colourD)
        self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
        self.window.refresh()
        self.window.attrset(0)

        # Buttons
        posy = h - 2
        posx = gap = int(((w - 2) - (8 + 7 + 8)) / 4) + 1
        self.chooseButton = ButtonBox(self, posy, posx, "Choose", 's',
                                      colour=colourB)
        posx = posx + 6 + gap
        self.clearButton = ButtonBox(self, posy, posx, "Clear", 'l',
                                     colour=colourB)
        posx = posx + 5 + gap
        self.cancelButton = ButtonBox(self, posy, posx, "Cancel", 'a',
                                      colour=colourB)

        # List of items
        if self.mode != self.SELECT:
            self.shortcuts = ['', '', 's', 'l', 'a']
            self.items = [self.dirListBox, self.fnameInput, self.chooseButton,
                          self.clearButton, self.cancelButton]
        else:
            self.shortcuts = ['', 's', 'l', 'a']
            self.items = [self.dirListBox, self.chooseButton, self.clearButton,
                          self.cancelButton]

    def _format_name(self, name, max_len):
        """Return a modified name if it is too long"""
        if len(name) > max_len:
            return name[:max_len - 5] + '(...)'
        else:
            return name

    def _count_files(self, path):
        size = 0
        for child in path.iterdir():
            size += 1
        return size

    def _populate(self, directory):
        """Update ListBox contents"""
        d = Path(directory)
        if d.is_dir():
            self.dirListBox.add_item('.   [current directory]', 1, str(d),
                                     scroll=False)
            if d != Path('/'):
                p = (d / '..').resolve()
                self.dirListBox.add_item('..  [parent directory]', 2, str(p),
                                         scroll=False)
            idx = 3
            size = self._count_files(d)  # Number if files in the the directory
            for child in d.iterdir():
                label = child.name
                length = self.dirListBox.w - 5  # Item's ListBox width
                if child.is_dir(): length -= 1  # If child is a directory
                label = self._format_name(label, length)
                if child.is_dir(): label += "/"  # If child is a directory
                last = size == idx - 2
                self.dirListBox.add_item(label, idx, str(child), scroll=last)
                idx += 1

    def update(self, item):
        """
        Update window according the filename selected.
        This method is called by the ListBox widget instance
        """
        if isinstance(item, Component) and item.has_focus():
            idx, path = item.get_data()
            path = Path(path)
            if path.is_dir():
                self.fnameInput.clear()
            elif self.mode == self.SELECT or self.mode == self.OVERWRITE:
                self.fnameInput.update(self._format_name(path.name, self.w - 21))

    def start(self, timeout=-1):
        """See mother class"""
        while True:
            result = TitledBorderWindow.start(self)  # Default controller

            # ListBox selected
            if result == self.dirListBox:
                result = self.dirListBox.start()

                # Escape
                if result is False:
                    self.index += 1  # Next widget (editor or button)
                    curses.ungetch(curses.ascii.ESC)  # Simulate escape window

                # Directory or normal file selected
                elif isinstance(result, Component):
                    idx, path = result.get_data()

                    # Current directory
                    if idx == 1:
                        if self.mode == self.CREATE \
                                or self.mode == self.OVERWRITE:
                            self.dirListBox.focus_off()
                            self.directory = path
                            self.index += 1  # Go to the editor

                    # A normal file or a directory
                    else:
                        if Path(path).is_dir():
                            try:
                                self.dnameLabel.update(
                                    self._format_name(path, self.w - 15))
                                self.dirListBox.clear_content()
                                self.directory = path
                                self._populate(path)
                            except PermissionError:
                                pass
                        else:
                            self.dirListBox.focus_off()
                            self.index += 1  # Next widget (editor or button)

                # Next or previous component
                elif result == 1 or result == -1:
                    self.dirListBox.focus_off()
                    self.index += result

            # Next item after editor
            elif result == self.fnameInput:
                result.focus_off()
                self.index = (self.index + 1) % len(self.items)

            # Cancel login window
            elif result is False or result == self.cancelButton:
                self.close()
                return False

            # Clear all input boxes
            elif result == self.clearButton:
                self.clearButton.focus_off()
                self.fnameInput.clear()
                self.index = 0

            # Try to return full filename
            elif result == self.chooseButton:

                # No inputs or selection ?
                if self.fnameInput.value is None:
                    self.chooseButton.focus_off()
                    self.index = 0

                else:
                    full_filename = self.directory + "/" + self.fnameInput.value

                    # Mode OVERWRITE : filename can exist or not
                    if self.mode == self.OVERWRITE:
                        self.close()
                        return full_filename

                    # Mode SELECT : OK if the filename exists
                    elif self.mode == self.SELECT \
                            and Path(full_filename).exists():
                        self.close()
                        return full_filename

                    # Mode CREATE : OK if the filename does not exist
                    elif self.mode == self.CREATE \
                            and not Path(full_filename).exists():
                        self.close()
                        return full_filename

                    # Go back to he editor
                    else:
                        self.chooseButton.focus_off()
                        self.index -= 1

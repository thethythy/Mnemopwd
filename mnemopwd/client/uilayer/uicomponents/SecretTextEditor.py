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

"""Simple secret text editing widget (only one line)"""

import curses
import time
from .TextEditor import TextEditor


class SecretTextEditor(TextEditor):
    """A secret text editor"""
    def __init__(self, win):
        TextEditor.__init__(self, win)
        self.maxy = 0    # A SecretInputBox works with only one line
        self.stext = ""  # The secret text

    def edit(self, validate=None):
        """Edit in the widget window and collect the results."""
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.win.refresh()
             
            y, x = self.win.getyx()
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE, curses.ascii.EOT):
                self.stext = self.stext[:x] + self.stext[x+1:]
            else:
                time.sleep(0.125)  # Wait 1/5 second before mask key
                if ch < 128:
                    self.stext = self.stext + \
                                 (self.win.instr(0, x - 1, 1)).decode()
                elif ch < 256:
                    self.stext = self.stext + \
                                 (self.win.instr(0, x - 1, 2)).decode()
                if x > 0:
                    self.win.addstr(y, x - 1, chr(0x2666))  # Mask key
                self.win.move(y, x)
        
        return self.stext

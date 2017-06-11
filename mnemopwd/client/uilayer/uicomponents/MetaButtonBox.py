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

from .ButtonBox import ButtonBox


class MetaButtonBox(ButtonBox):
    """A button box with a user data"""

    def __init__(self, parent, y, x, label, shortcut=None, show=True, data=None,
                 colour=False):
        """Object initialization"""
        if show:
            ButtonBox.__init__(self, parent, y, x, label, shortcut=shortcut,
                               show=show, colour=colour)
        else:
            self.label = ' ' + label + ' '
            self.parent = parent
            self.y = y
            self.x = x
            self.shortcut = shortcut
            self.modal = False
            self.showOrHide = show
            self.colour = colour
        self.data = data

    def move(self, y, x, focus=False):
        """See mother class"""
        self.y = y
        self.x = x

    def show(self):
        """See mother class"""
        self.showOrHide = True
        self._create(False)

    def set_data(self, data):
        """Set user data"""
        self.data = data

    def get_data(self):
        """Get user data"""
        return self.data

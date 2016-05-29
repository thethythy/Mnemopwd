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

from client.uilayer.uicomponents.BaseWindow import BaseWindow
from client.uilayer.uicomponents.ButtonBox import ButtonBox
from client.util.funcutils import sfill

class CreateMenu(BaseWindow):
    """
    The menu for creating a new entry in the database
    """
    
    def __init__(self, parent, btypes, y, x):
        """Create the menu"""
        # Create the window
        max_len = 0
        for type in btypes.values(): max_len = max(max_len, len((type["1"])["name"]))
        BaseWindow.__init__(self, parent, len(btypes), max_len + 3, y, x, menu=True, modal=True)
        self.window.refresh()
        
        # Add buttons (preserving the order indicated in the json file)
        posy = 0
        for i in range(1, len(btypes) + 1):
            name = ((btypes[str(i)])["1"])["name"]
            self.items.append(ButtonBox(self, posy, 0, name + sfill(max_len - len(name))))
            posy += 1
            
    def start(self):
        while True:
            # Interaction loop
            result = BaseWindow.start(self)
            
            # Escape
            if result == False:
                self.close()
                return False
            
            # Return the number of block type selected
            else:
                self.close()
                return self.index + 1

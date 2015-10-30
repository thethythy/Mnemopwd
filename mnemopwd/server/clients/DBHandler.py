# -*- coding: utf-8 -*-

# Copyright (c) 2015, Thierry Lemeunier <thierry at lemeunier dot net>
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


"""
Database Handler
"""

import os
import os.path
import stat
import shelve
import re
from server.util.Configuration import Configuration

class DBHandler:
    """Database handler"""
    
    # Intern methods
    
    def __init__(self, path, filename):
        """Set attributs"""
        self.path = path                # Client database path
        self.filename = filename        # Client database filename
        
    def __getitem__(self, index):
        """Get an item. Raise KeyError exception if index does not exist"""
        with shelve.open(self.path + '/' + self.filename, flag='r') as db:
            value = db[index]
        return value
    
    def __setitem__(self, index, value):
        """Set an item"""
        with shelve.open(self.path + '/' + self.filename, flag='w') as db:
            db[index] = value

    # Extern methods
    
    @staticmethod
    def new(path, filename):
        """Try to create a new db"""
        if DBHandler.exist(path, filename) :
            return False
        else:
            # Create a new database file with good permissions
            with shelve.open(path + '/' + filename, flag='n') as db:
                db['nbsibs'] = 0
            os.chmod(path + '/' + filename + '.db', \
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
            return True
    
    @staticmethod
    def exist(path, filename):
        """Test if the data file exist"""
        return os.path.exists(path + '/' + filename + '.db')
        
    def add_data(self, sib):
        """Add a secret information block and return his index (a string)"""
        nbsibs = self['nbsibs'] + 1   # Increment the number of block
        self['nbsibs'] = nbsibs       # Store the new number of block
        index = str(nbsibs)           # The index
        self[index] = sib             # Store the block
        return index                  # Return the index of the block
        
    def search_data(self, keyH, pattern):
        """Search secret information matching the pattern"""
        tabsibs = []                # Table of sibs
        nbsibs = self['nbsibs']     # Number of sibs
        if nbsibs > 0:
            for i in range(1, nbsibs + 1): # For all sibs
                sib = self[str(i)]  # Get sib
                sib.keyH = keyH     # Set actual keyhandler
                if sib.nbInfo > 0 :
                
                    if Configuration.search_mode == 'first' :
                        if re.search(pattern, sib['info1'].decode()) is not None :
                            tabsibs.append((i,sib)) # Pattern matching so add sib in table
                    else:
                        for j in range(1, sib.nbInfo + 1) : # For all info in sib
                            if re.search(pattern, sib['info' + str(j)].decode()) is not None :
                                tabsibs.append((i,sib)) # Pattern matching so add sib in table
                                break
        return tabsibs

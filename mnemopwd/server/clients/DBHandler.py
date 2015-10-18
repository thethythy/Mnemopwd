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

class DBHandler:
    """Database handler"""
    
    # Intern methods
    
    def __init__(self, path, filename):
        """Set attributs"""
        self.database_file = path + '/' + filename # Client database file

    def __getitem__(self, index):
        """Get an item. Raise KeyError exception if index does not exist"""
        with shelve.open(self.database_file, flag='r') as db:
            value = db[index]
        return value
    
    def __setitem__(self, index, value):
        """Set an item"""
        with shelve.open(self.database_file, flag='w') as db:
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
                db['nb_sibs'] = 0
            os.chmod(path + '/' + filename + '.db', \
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
            return True
    
    @staticmethod
    def exist(path, filename):
        """Test if the data file exist"""
        return os.path.exists(path + '/' + filename + '.db')
        
    def add_data(self, sib):
        """Add a secret information block and return his index (a string)"""
        nb_sibs = self['nb_sibs'] + 1   # Increment the number of block
        self['nb_sibs'] = nb_sibs       # Store the new number of block
        index = str(nb_sibs)            # The index
        self[index] = sib               # Store the block
        return index                    # Return the index of the block

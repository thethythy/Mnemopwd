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

A database is a shelf object: a persistent dictonary stored in a database file
(see module shelve for more explanations).

Each shelf have at least two entries : 'nbsibs' for the number of sibs stored (must be
incremented or decremented) and 'index' for the last index used (must only be incremented)

An example of a shelve: 
    {
        'nbsibs': 4 (it means that there are exactly 4 sibs in the database) 
        'index' : 5 (it means that the next entry will have 6 for index) 
        '1' : a sib
        '2' : a sib
        '4' : a sib (it means that a sib has been deleted before this entry)
        '5' : a sib
    }

"""

import os
import os.path
import stat
import shelve
import re
import threading
from server.util.Configuration import Configuration

class DBHandler:
    """Database handler
    
    Attribut(s):
    - lock: a threading.Lock instance to control database access (class attribut)
    - path: a string for the database directory (instance attribut)
    - filename: a string for the databse file name (instance attribut)
    
    Method(s):
    - new: a static method for database creation
    - exist: a static method for testing if a database already exist
    - add_data: a method for adding a secret information block in database
    - search_data: a method for searching secret information blocks matching a pattern
    - update_data: a method for updating a secret information block in database
    """
    
    lock = threading.Lock()             # Lock object for control database access
    
    # Intern methods
    
    def __init__(self, path, filename):
        """Set attributs"""
        self.path = path                # Client database path
        self.filename = filename        # Client database filename
        
    def __getitem__(self, index):
        """Get an item. Raise KeyError exception if index does not exist"""
        with DBHandler.lock:
            with shelve.open(self.path + '/' + self.filename, flag='r') as db:
                value = db[index]
        return value
    
    def __setitem__(self, index, value):
        """Set an item"""
        with DBHandler.lock:
            with shelve.open(self.path + '/' + self.filename, flag='w') as db:
                db[index] = value
                
    def __delitem__(self, index):
        """Delete an item. Raise KeyError exception if index does not exist"""
        with DBHandler.lock:
            with shelve.open(self.path + '/' + self.filename, flag='w') as db:
                del db[index]

    # Extern methods
    
    @staticmethod
    def new(path, filename):
        """Try to create a new db. Return a boolean."""
        if DBHandler.exist(path, filename) :
            return False
        else:
            # Create a new database file with good permissions
            with shelve.open(path + '/' + filename, flag='n') as db:
                db['nbsibs'] = 0  # Number of secret information blocks
                db['index'] = 0   # Last entry index
            os.chmod(path + '/' + filename + '.db', \
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
            return True
    
    @staticmethod
    def exist(path, filename):
        """Test if the database file exist"""
        return os.path.exists(path + '/' + filename + '.db')
        
    def add_data(self, sib):
        """Add a secret information block and return his index (a string)"""
        nbsibs = self['nbsibs'] + 1   # Increment the number of block
        self['nbsibs'] = nbsibs       # Store the new number of block
        index = self['index'] + 1     # Increment the index
        self['index'] = index         # Store the new index
        index = str(index)            # index as string
        self[index] = sib             # Store the block
        return index                  # Return the index of the block
        
    def search_data(self, keyH, pattern):
        """Search secret information matching the pattern. Return a list of sib found."""
        tabsibs = []                # Table of sibs
        nbsibs = self['nbsibs']     # Number of sibs
        if nbsibs > 0: 
            for i in range(1, nbsibs + 1): # For all sibs
                try:
                    sib = self[str(i)]  # Get sib (can raise a KeyError exception)
                    sib.keyH = keyH     # Set actual KeyHandler
                    if sib.nbInfo > 0 :
                        if Configuration.search_mode == 'first' :
                            if re.search(pattern, sib['info1'].decode()) is not None :
                                tabsibs.append((i,sib)) # Pattern matching so add sib in table
                        else:
                            for j in range(1, sib.nbInfo + 1) : # For all info in sib
                                if re.search(pattern, sib['info' + str(j)].decode()) is not None :
                                    tabsibs.append((i,sib)) # Pattern matching so add sib in table
                                    break # One info match so stop loop now
                except KeyError:
                    pass
        return tabsibs
        
    def update_data(self, index, sib):
        """Update a secret information block. Return a boolean."""
        try:
            index = int(index)      # Conversion in int (can raise a ValueError exception)
            index = str(index)      # index as a string type
            oldsib = self[index]    # Get actual sib (can raise a KeyError exception)
            self[index] = sib       # Set updated sib
            return True
        except ValueError:
            return False
        except KeyError:
            return False
    
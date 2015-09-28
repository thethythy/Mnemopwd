# -*- coding: utf-8 -*-

# Copyright (C) 2015 Thierry Lemeunier <thierry at lemeunier dot net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        self.database_file = path + filename + '.db' # Client database file

    # Extern methods
    
    @staticmethod
    def new(path, filename):
        """Try to create a new db"""
        print('hello world')
        
        if DBHandler.exist(path, filename) :
            return False
        else:
            # Create a new database file with good permissions
            with shelve.open(path + filename, flag='n') as db: db['nb_sibs'] = 0
            os.chmod(path + filename + '.db', stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
            return True
    
    @staticmethod
    def exist(path, filename):
        """Test if the data file exist"""
        print("hello world 2", filename)
        return os.path.exists(path + filename + '.db')
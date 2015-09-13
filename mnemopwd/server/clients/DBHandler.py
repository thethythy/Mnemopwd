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

import shelve

class DBHandler:
    """Database handler"""
    
    # Intern methods
    
    def __init__(self, path, id):
        """Set attributs"""
        self.path = path # Path to the db directory
        self.id = id # db name is id
        
    # Extern methods
    
    @staticmethod
    def new(path, id):
        """Try to create a new db"""
        print('hello world')
        
        with shelve.open(path + id, flag='n') as db:
            db['nb_sibs'] = 0
            
        return True
    
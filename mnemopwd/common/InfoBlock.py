# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
The class InfoBlock stores information.
"""

import logging
import re


class InfoBlock:
    """
    Dictionary of information
    
    Property(ies):
    - infos : a dictionary like {"infoX" : "cypher text",...}
              where 'X' is an integer <= nbInfo
    - nbInfo : integer indicating the maximum of secret information stored
    
    Attribute(s):
    - _infos : do not directly access to this attribute but use infos property
    - _nbInfo : do not directly access to this attribute but use nbInfo property
    
    Method(s): none
    
    """

    def __init__(self, nbInfo=1):
        """Object initialization.
        By default, the number of secret information is set to one."""
        self._infos = {}        # Empty dict
        self._nbInfo = nbInfo   # Number of secret information

    # Properties
    # ----------

    # Property infos

    @property
    def infos(self):
        """Return the dictionary"""
        return self._infos
    
    @infos.setter
    def infos(self, value):
        """Do nothing"""
        logging.warning("It is not permit to change the value of 'infos' property")
    
    @infos.deleter
    def infos(self):
        """Do nothing"""
        logging.warning("It is not permit to delete the 'infos' property")

    # Property nbInfo

    @property
    def nbInfo(self):
        """Getter method of the nbInfo property"""
        return self._nbInfo

    @nbInfo.setter
    def nbInfo(self, nbInfo):
        """"Setter method of the nbInfo property.
        Attention : if the new size is inferior to the old size, last entries
        are deleted.
        Attention : the parameter must be an integer > 0 ;
        if not it raises AssertionError exception"""
        # Verify the validity of the parameter
        assert isinstance(nbInfo, int) and nbInfo > 0
        if nbInfo < self._nbInfo:
            logging.critical(
                "InfoBlock: size decreased (%s/%s). Next information deleted :",
                nbInfo, self._nbInfo)
        while nbInfo < self._nbInfo:
            infoX = "info" + str(self._nbInfo) 
            logging.critical("%s : %s", infoX, self._infos[infoX])
            del self._infos[infoX]  # Delete entry with key > nbInfo
            self._nbInfo -= 1
        self._nbInfo = nbInfo   # Change the number of information
        
    @nbInfo.deleter
    def nbInfo(self):
        """Do nothing"""
        logging.warning("It is not permit to delete the 'nbInfo' property")

    # Intern methods
    # --------------
    
    def __getstate__(self):
        """Returns the object's state"""
        return self.__dict__
    
    def __setstate__(self, state):
        """Restores the object's state"""
        self.__dict__.update(state)

    def _verify_index_(self, index):
        """Verifies if the index parameter is a valid index format"""
        if not isinstance(index, str):
            logging.error("InfoBlock: index parameter %s must be a string",
                          str(index))
            raise TypeError("index parameter must be a string")
        index_regex = "^info[1-" + str(self.nbInfo) + "]$"
        if re.search(index_regex, index) is None:
            logging.error("InfoBlock: index parameter %s is not correct", index)
            raise KeyError("index parameter is not correct")
    
    def __getitem__(self, index):
        """Returns the value corresponding to the index if it exists and
        it is valid otherwise raises a KeyError exception"""
        self._verify_index_(index)  # Verify if the index parameter is valid
        return self.infos[index]
    
    def __setitem__(self, index, value):
        """Stores the value at the index given if the index is valid otherwise
        raises a KeyError exception"""
        self._verify_index_(index)  # Verify if the index parameter is valid
        self.infos[index] = value

    def __delitem__(self, index):
        """Deletes the entry corresponding to the index if it exists otherwise
        raises a KeyError exception"""
        self._verify_index_(index)  # Verify if the index parameter is valid
        del self.infos[index]

    def __contains__(self, value):
        """Tests if the value exists at least in one entry.
        Warning : it is not the usual behaviour (that works usually on keys
        not on values)"""
        for key in self.infos:
            if self[key] == value:
                return True
        return False
    
    def __len__(self):
        """Returns the number of entries. It is always >= 0 and <= nbInfo.
        It raises an AssertionError exception if it is not the case"""
        size = len(self.infos)
        condition = 0 <= size <= self.nbInfo
        if not condition:
            logging.critical("InfoBlock: size is not correct : %s / %s",
                             str(size), self.nbInfo)
        assert condition 
        return size

    def __iter__(self):
        """Return an iterator"""
        self._iter_counter = 0
        return self

    def __next__(self):
        """Returns the next element or raises StopIteration"""
        if self._iter_counter == self.nbInfo:
            raise StopIteration
        self._iter_counter += 1
        return self['info' + str(self._iter_counter)]

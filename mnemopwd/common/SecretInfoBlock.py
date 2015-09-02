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

The class SecretInfoBlock stores secret informations.

A secret information is a cypher text encrypted with the ECIES scheme.

Each secret information is stored in a dictionnary. The key of each entry
is a string with the forme 'infoX' where 'X' is a integer. The 'X' value
depends on the maximum number of secret informations stored by the object.

Global integrity is controlled by a hmac (512 bits) performed at save time and
controlled at load time. This treatment is done by server part of the application.

"""

import logging
import re
from common.CryptoHandler import CryptoHandler

class SecretInfoBlock:
    """
    Dictionnary of secret informations
    
    Property(ies):
    - infos : a dictionary like {"infoX" : "cyper text",...} where 'X' is an integer <= nbInfo
    - nbInfo : integer indicating the maximum of secet informations stored
    
    Attribut(s): none
    
    Method(s): none
    
    """

    def __init__(self, nbInfo=1):
        """Object initialization. By default, the number of secret informations is set to one."""
        self._infos = {}        # Empty dict
        self._nbInfo = nbInfo   # Number of secret informations

    # Properties
    # ----------

    # Property infos

    @property
    def infos(self):
        return self._infos
    
    @infos.setter
    def infos(self, value):
        logging.warning("It is not permit to change the value of 'infos' property")
    
    @infos.deleter
    def infos(self):
        logging.warning("It is not permit to delete the 'infos' property")

    # Property nbInfo

    @property
    def nbInfo(self):
        """Getter method of the nbInfo property"""
        return self._nbInfo

    @nbInfo.setter
    def nbInfo(self, nbInfo):
        """"Setter method of the nbInfo property.
        Attention : if the new size is inferior to the old size, last entries are deleted.
        Attention : the parameter must be an integer > 0 ; if not it raises AssertionError exception"""
        assert isinstance(nbInfo, int) and nbInfo > 0   # Verify the validity of the parameter
        if nbInfo < self._nbInfo :
            logging.critical("The size of a SecretInfoBlock object has decrased (%s/%s). Next secrets are deleted :", nbInfo, self._nbInfo)
        while nbInfo < self._nbInfo :
            infoX = "info" + str(self._nbInfo) 
            logging.critical("%s : %s", infoX, self._infos[infoX])
            del self._infos[infoX]  # Delete entry with key > nbInfo
            self._nbInfo -= 1
        self._nbInfo = nbInfo   # Change the number of informations
        
    @nbInfo.deleter
    def nbInfo(self):
        logging.warning("It is not permit to delete the 'nbInfo' property")

    # Intern methods
    # --------------
    
    @CryptoHandler.compute_integrity_siblock
    def __getstate__(self):
        """Returns the object's state"""
        return self.__dict__
    
    @CryptoHandler.control_integrity_siblock
    def __setstate__(self, state):
        """Restores the objet's state"""
        self.__dict__.update(state)

    def _verify_index_(self, index):
        """Verifies if the index parameter is valid index format"""
        if not isinstance(index, str) :
            logging.error("In SecretInfoBlock index paramter %s must be a string", str(index))
            raise TypeError("index parameter must be a string")
        index_regex = "^info[1-" + str(self.nbInfo) + "]$"
        if re.search(index_regex, index) is None :
            logging.error("In SecretInfoBlock index paramter %s is not correct", index)
            raise KeyError("index parameter is not correct")
    
    @CryptoHandler.decrypting_value(0)  # Decryption stage 1 
    @CryptoHandler.decrypting_value(1)  # Decryption stage 2
    @CryptoHandler.decrypting_value(2)  # Decryption stage 3
    def __getitem__(self, index):
        """Returns the value corresponding to the index if it exists and it is valid otherwise raises a KeyError exception"""
        self._verify_index_(index) # Verify if the index parameter is valid
        return self.infos[index]
    
    @CryptoHandler.encrypting_value(0)  # Encryption stage 1
    @CryptoHandler.encrypting_value(1)  # Encryption stage 2
    @CryptoHandler.encrypting_value(2)  # Encryption stage 3
    def __setitem__(self, index, value):
        """Stores the value at the index given if the index is valid otherwise raises a KeyError exception"""
        self._verify_index_(index) # Verify if the index parameter is valid
        self.infos[index] = value

    def __delitem__(self, index):
        """Deletes the entry corresponding to the index if it exists otherwise raises a KeyError exception"""
        self._verify_index_(index) # Verify if the index parameter is valid
        del self.infos[index]

    def __contains__(self, value):
        """Tests if the value exists at least in one entry.
        Attention : it is not the usual behaviour (that works usually on keys not on values)"""
        for key, value in self.infos.items() :
            if self.infos[key] == value :
                return True
        return False
    
    def __len__(self):
        """Returns the number of entries. It is always >= 0 and <= nbInfo.
        It raises an AssertionError exception if it is not the case"""
        size = len(self.infos)
        condition = 0 <= size <= self.nbInfo
        if not(condition) :
            logging.critical("The size of a SecretInfoBlock object is not correct : %s / %s", str(size), self.nbInfo)
        assert condition 
        return size
    
    # Extern methods
    # --------------
    
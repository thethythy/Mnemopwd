# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016, Thierry Lemeunier <thierry at lemeunier dot net>
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
The class SecretInfoBlock stores secret information.

A secret information is a cypher text encrypted with the ECIES scheme.

Each secret information is stored in a dictionary. The key of each entry
is a string with the form 'infoX' where 'X' is a integer. The 'X' value
depends on the maximum number of secret information stored by the object.

Global integrity is controlled by a hmac (512 bits) performed before storing and
controlled after loading. This treatment is done by server part of
the application.
"""

import logging
from .InfoBlock import InfoBlock
from ..pyelliptic import hash


class SecretInfoBlock(InfoBlock):
    """
    Dictionary of secret information.
    It is a subclass of InfoBlock.
    
    Property(ies): none
    
    Attribute(s):
    - keyH: a KeyHandler object (never saved)
    
    Method(s):
    - control_integrity: a method used to control fingerprint value
    
    """
    
    # Intern methods
    # --------------

    def __init__(self, keyH=None, nbInfo=1):
        """Object initialization.
        By default, the number of secret information is set to one."""
        InfoBlock.__init__(self, nbInfo)
        self.keyH = keyH
    
    def __sorted_state__(self, state):
        """Return a bytes string from a sorted list of the state"""
        # Get the secret information
        state_list = list(state['_infos'].items())
        # Get the number of secret information
        state_list.append(('_nbInfo', state['_nbInfo']))
        state_list.sort()  # Sort the list
        return str(state_list).encode()  # Transform the list to a bytes string

    def __getstate__(self):
        """Returns the object's state after computing the integrity value"""
        state = self.__dict__.copy()
        del state["keyH"]  # Delete KeyHandler object reference
        try:
            del state["fingerprint"]  # Delete old fingerprint entry
        except KeyError:
            pass
        # Compute hmac with the key handler
        message = self.__sorted_state__(state) + self.keyH.config.encode()
        state["fingerprint"] = hash.hmac_sha512(self.keyH.ikey, message)
        return state
    
    def __setstate__(self, state):
        """Restores the objet's state"""
        self.__dict__.update(state)
        
    def __getitem__(self, index):
        """Decrypt value after being restored from a block"""
        self._verify_index_(index)  # Verify if the index parameter is valid
        cleartext1 = self.keyH.decrypt(2, self.infos[index])
        cleartext2 = self.keyH.decrypt(1, cleartext1)
        cleartext = self.keyH.decrypt(0, cleartext2)
        return cleartext
    
    def __setitem__(self, index, value):
        """Encrypt value before being stored in a block"""
        self._verify_index_(index)  # Verify if the index parameter is valid
        ciphertext1 = self.keyH.encrypt(0, value)
        ciphertext2 = self.keyH.encrypt(1, ciphertext1)
        ciphertext = self.keyH.encrypt(2, ciphertext2)
        self.infos[index] = ciphertext
        
    # Extern methods
    # --------------
    
    def control_integrity(self, keyH):
        """Control integrity. Must be call only once after __setstate__
        If integrity control fails, an AssertionError is raised."""
        state = self.__dict__
        
        # Store the fingerprint
        fingerprint = state["fingerprint"]
        
        # Delete the fingerprint entry
        del state["fingerprint"]
        
        # Compute the hmac
        message = self.__sorted_state__(state) + keyH.config.encode()
        hmac = hash.hmac_sha512(keyH.ikey, message)
        
        # The hmac must be equal to the fingerprint 
        condition = hash.equals(fingerprint, hmac)
        if not condition:
            logging.critical("Intergrity checking fails on a SecretInfoBlock object")
        assert condition
        
        self.keyH = keyH  # Store the key handler

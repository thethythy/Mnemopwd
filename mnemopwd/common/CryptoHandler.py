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
CryptoHandler is in charge of cyryptographic operations.
""" 

import logging
from pyelliptic import hash as _hash

class CryptoHandler:
    """
    CryptoHandler is the handler of cryptographic operations for a client.
    
    Class attribut(s):
    - keyH : a KeyHandler object
    """
    
    keyH = None # The client's key handler object
    
    # Intern methods
    # --------------
    
    def __init__(self, keyH):
        """Intialiaze the object
        keyH : a key handler object
        """
        CryptoHandler.keyH = keyH
    
    # Extern methods
    # --------------
    
    @staticmethod
    def compute_integrity_siblock(function):
        """Computes the global integrity value of a SecretInfoBlock object"""
        
        def decorated_function(*args, **kwargs):
            state = function(*args, **kwargs)   # Get the normal state
            try:
                del state["fingerprint"]    # Delete old fingerprint entry
            except:
                pass
            state["fingerprint"] = _hash.hmac_sha512(CryptoHandler.keyH.ikey, (str(state)).encode()) # Compute hmac with the key's handler
            return state # Return the state with the integrity entry
        
        return decorated_function

    @staticmethod
    def control_integrity_siblock(function):
        """Controls the global integrity of a SecretInfoBlock object.
        If integrity control fails, an AssertionError is raised."""
        
        def decorated_function(*args, **kwargs):
            state = args[1] # The state is the second argument
            fingerprint = state["fingerprint"]  # Store the fingerprint
            del state["fingerprint"] # Del the fingerprint entry to compute the hmac
            hmac = _hash.hmac_sha512(CryptoHandler.keyH.ikey, (str(state)).encode()) # Compute the hmac
            condition = _hash.equals(fingerprint, hmac) # The computed hmac must be equal to the fingerprint 
            if not condition :
                logging.critical("Intergrity checking fails on a SecretInfoBlock object")
            assert condition
            return function(*args, **kwargs) # Call the normal function to change state
        
        return decorated_function
    
    @staticmethod
    def encrypting_value(stage):
        """Encrypt value before being stored in a block"""
        def intern_decorator(function):
            def decorated_function(*args, **kwargs):
                value = args[2] # The value is the third argument
                newargs = args[0], args[1], CryptoHandler.keyH.encrypt(stage, value)
                return function(*newargs, **kwargs) # Call the normal function with a cipher text
            return decorated_function
        return intern_decorator
        
    @staticmethod
    def decrypting_value(stage):
        """Decrypt value after being restored from a block"""
        def intern_decorator(function):
            def decorated_function(*args, **kwargs):
                cyphertext = function(*args, **kwargs) # Call the normal function to get the cipher text
                return CryptoHandler.keyH.decrypt(stage, cyphertext) # Return a clear text
            return decorated_function
        return intern_decorator
    
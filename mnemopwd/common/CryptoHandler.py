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
    
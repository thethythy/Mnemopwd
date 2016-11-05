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
Class to create and handle keys to encrypt, decrypt and check integrity
"""

import hashlib

from ..pyelliptic import ECC


class KeyHandler:
    """Create and handle keys to crypt, decrypt and check integrity
   
    Attribute(s) :
    - ikey : key for integrity operations (bytes array)
    - config : string of the cryptographic suite
    - eccs : list of dictionaries of ECC object and cipher name
      For example, for stage one :
            eccs[0] == {'ecc':ECC_object, 'cipher':'cipher_name'}
    """
    
    # Intern methods
    # --------------

    def __init__(self, msecret,
                 cur1='sect571r1', cip1='aes-256-cbc',
                 cur2='', cip2='', cur3='', cip3=''):
        """Object initializer"""
        # Compute ikey
        ho = hashlib.sha512()
        ho.update(msecret)
        self.ikey = ho.digest()  # The key for integrity operations
        
        # Create ECC objects
        self.config = cur1 + ";" + cip1 + ";" + \
            cur2 + ";" + cip2 + ";" + \
            cur3 + ";" + cip3
        self.eccs = []  # The list to store ECC objects and cipher names
        # The first stage ECC
        self.eccs.append({
            'ecc': self._compute_ecc_(cur1, msecret, 'first'),
            'cipher': cip1
        })
        # The second stage ECC
        self.eccs.append({
            'ecc': self._compute_ecc_(cur2, msecret, 'second'),
            'cipher': cip2
        })
        # The third stage ECC
        self.eccs.append({
            'ecc': self._compute_ecc_(cur3, msecret, 'third'),
            'cipher': cip3})

    def _get_ecc_(self, index):
        """Returns the tuple (ECC_object, 'cipher_name').
        If index is not valid, raises an AssertionException exception"""
        assert 0 <= index < 3
        return (self.eccs[index])['ecc'], (self.eccs[index])['cipher']

    def _compute_ecc_(self, curve, secret, stagename):
        """Creates a new ECC object"""
        if curve == '':
            return None
        else:
            ho = hashlib.sha512()
            ho.update(secret)
            ho.update("the %s stage ecc secret".format(stagename).encode())
            pubx, puby, priv = ECC.compute_keypair(ho.digest(), curve)
            return ECC(
                pubkey_x=pubx, pubkey_y=puby, raw_privkey=priv, curve=curve)

    # Extern Methods
    # --------------

    def encrypt(self, stage, cleartext):
        """Encryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None:
            return ecc.encrypt(cleartext, ecc.get_pubkey(),
                               ephemcurve=ecc.get_curve(),
                               ciphername=ciphername)
        else:
            return cleartext
    
    def decrypt(self, stage, cyphertext):
        """Decryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None:
            return ecc.decrypt(cyphertext, ciphername=ciphername)
        else:
            return cyphertext

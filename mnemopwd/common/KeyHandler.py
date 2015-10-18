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
Class to create and handle keys to encrypt, decrypt and check integrity
"""

from pyelliptic import OpenSSL, ECC
import hashlib
import logging

class KeyHandler:
    """Create and handle keys to crypt, uncrypt and chech integrity
   
    Attribut(s) :
    - ikey : key for integrity operations (bytes array)
    - config : string of the cryptographic suite
    - eccs : list of dictionaries of ECC object and cipher name for operations of each stage
      For example, for stage one : eccs[0] == {'ecc':ECC_object, 'cipher':'cipher_name'}
    """
    
    # Intern methods
    # --------------
    
    def __init__(self, msecret, cur1='sect571r1', cip1='aes-256-cbc', cur2='', cip2='', cur3='', cip3=''):
        """Object initializer"""
        # Compute ikey
        ho = hashlib.sha512()
        ho.update(msecret)
        self.ikey = ho.digest() # The key for integrity operations
        
        # Create ECC objects
        self.config = cur1 + ";" + cip1 + ";" + cur2 + ";" + cip2 + ";" + cur3 + ";" + cip3
        self.eccs = [] # The list to store ECC objects and cipher names
        self.eccs.append({'ecc':self._compute_ecc_(cur1, msecret, 'first'), 'cipher':cip1}) # The first stage ECC
        self.eccs.append({'ecc':self._compute_ecc_(cur2, msecret, 'second'), 'cipher':cip2}) # The second stage ECC
        self.eccs.append({'ecc':self._compute_ecc_(cur3, msecret, 'third'), 'cipher':cip3}) # The thrid stage ECC

    def _get_ecc_(self, index):
        """Returns the tuple (ECC_object, 'cipher_name').
        If index is not valid, raises an AssertionException exception"""
        assert 0 <= index < 3
        return (self.eccs[index])['ecc'], (self.eccs[index])['cipher']

    @staticmethod
    def _compute_keypair_(cur, secret):
        """Computes a keypair from a secret number.
        If secret >= cur.order then secret is truncated until it becomes false"""
        try:
            # Create a BIGNUM structure (see OpenSSL documentation) from the secret number
            bn_secret = OpenSSL.BN_bin2bn(secret, len(secret), 0)
                     
            # Create a keypair structure (see OpenSSL documentation) from a curve name
            ec_key = OpenSSL.EC_KEY_new_by_curve_name(OpenSSL.get_curve(cur))
            if ec_key == 0:
                raise Exception("EC_KEY_new_by_curve_name fails with %s".format(cur))
            
            # Get the group of the curve
            ec_group = OpenSSL.EC_KEY_get0_group(ec_key)
            
            # Create a new point structure (see OpenSSL documentation) on the curve to store pubkey
            ec_point = OpenSSL.EC_POINT_new(ec_group)
            
            # Create a new context structure (see OpenSSL documentation) for next treatments
            bn_ctx = OpenSSL.BN_CTX_new()
            
            # Control that secret < order
            bn_order = OpenSSL.BN_new() # Create a BIGNUM structure to store order
            OpenSSL.EC_GROUP_get_order(ec_group, bn_order, bn_ctx); # Get the order
            while OpenSSL.BN_cmp(bn_secret, bn_order) >= 0 : # If secret >= order
                logging.warning("Decrease secret because it is > of order of the curve %s", cur)
                new_number_bits = (OpenSSL.BN_num_bytes(bn_secret) - 1) * 8 # Decrease the size by 8 bits
                OpenSSL.BN_mask_bits(bn_secret, new_number_bits) # Truncate
            
            # Compute the public key
            if OpenSSL.EC_POINT_mul(ec_group, ec_point, bn_secret, 0, 0, bn_ctx) == 0:
                raise Exception("EC_KEY_new_by_curve_name fails with %s".format(cur))
            
            # Verify the keypair
            if OpenSSL.EC_KEY_set_public_key(ec_key, ec_point) == 0:
                raise Exception("EC_KEY_set_public_key fails")
            if OpenSSL.EC_KEY_set_private_key(ec_key, bn_secret) == 0:
                raise Exception("EC_KEY_set_private_key fails")
            if OpenSSL.EC_KEY_check_key(ec_key) == 0:
                raise Exception("EC_KEY_check_key fails")
            
            # Get public key affine coordinates
            pub_key_x = OpenSSL.BN_new()
            pub_key_y = OpenSSL.BN_new()
            if OpenSSL.EC_POINT_get_affine_coordinates_GFp(ec_group, ec_point, pub_key_x, pub_key_y, 0) == 0:
                raise Exception("EC_POINT_get_affine_coordinates_GFp fails")
            
            # Allocate memories to return keypair
            privkey = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(bn_secret))
            pubkeyx = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(pub_key_x))
            pubkeyy = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(pub_key_y))
            OpenSSL.BN_bn2bin(bn_secret, privkey)
            privkey = privkey.raw
            OpenSSL.BN_bn2bin(pub_key_x, pubkeyx)
            pubkeyx = pubkeyx.raw
            OpenSSL.BN_bn2bin(pub_key_y, pubkeyy)
            pubkeyy = pubkeyy.raw

            return pubkeyx, pubkeyy, privkey

        finally:
            OpenSSL.BN_free(pub_key_x)
            OpenSSL.BN_free(pub_key_y)
            OpenSSL.BN_free(bn_order)
            OpenSSL.BN_CTX_free(bn_ctx)
            OpenSSL.EC_POINT_free(ec_point)
            OpenSSL.EC_KEY_free(ec_key)
            OpenSSL.BN_free(bn_secret)
    
    def _compute_ecc_(self, curve, secret, stagename):
        """Creates a new ECC object"""
        if curve == '':
            return None
        else:
            ho = hashlib.sha512()
            ho.update(secret)
            ho.update("the %s stage ecc secret".format(stagename).encode())
            pubx, puby, priv = KeyHandler._compute_keypair_(curve, ho.digest())
            return ECC(pubkey_x=pubx, pubkey_y=puby, raw_privkey=priv, curve=curve)
    
    # Extern Methods
    # --------------

    def encrypt(self, stage, cleartext):
        """Encryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None :
            return ecc.encrypt(cleartext, ecc.get_pubkey(), ephemcurve=ecc.get_curve(), ciphername=ciphername)
        else:
            return cleartext
    
    def decrypt(self, stage, cyphertext):
        """Decryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None :
            return ecc.decrypt(cyphertext, ciphername=ciphername)
        else:
            return cyphertext

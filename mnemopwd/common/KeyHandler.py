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
Class to create and handle keys to crypt, decrypt and check integrity
"""

from pyelliptic import OpenSSL, ECC
import hashlib
import logging

class KeyHandler:
    """Create and handle keys to crypt, uncrypt and chech integrity
   
    Attribut(s) :
    - ikey : key for integrity operations (bytes array)
    - eccs : sequence of dictionaries of ECC object and cipher name for operations of each stage
      For example, for stage one : eccs[0] == {'ecc':ECC_object, 'cipher':'cipher_name'}
    """
    
    # Intern methods
    # --------------
    
    def __init__(self, msecret, cur1='secp256k1', cip1='aes-256-cbc', cur2=None, cip2=None, cur3=None, cip3=None):
        """Object initializer"""
        # Compute ikey
        ho = hashlib.sha512()
        ho.update(msecret)
        self.ikey = ho.digest() # The key for integrity operations
        
        # Create ECC objects
        self.eccs = [] # The list to store ECC objects and cipher names
        self.eccs.append({'ecc':self._compute_ecc_(cur1, msecret, 'first'), 'cipher':cip1}) # The first stage ECC
        self.eccs.append({'ecc':self._compute_ecc_(cur2, msecret, 'second'), 'cipher':cip2}) # The second stage ECC
        self.eccs.append({'ecc':self._compute_ecc_(cur3, msecret, 'third'), 'cipher':cip3}) # The thrid stage ECC

    def _get_ecc_(self, index):
        """Returns the tuple (ECC_object, 'cipher_name').
        If index is not valid, raises an AssertionException exception"""
        assert 0 <= index < 3
        return (self.eccs[index])['ecc'], (self.eccs[index])['cipher']
    
    def _compute_keypair_(self, cur, secret):
        """Computes a keypair from a secret number.
        If secret >= cur.order then secret is truncated until it becomes false.
        OpenSSL library makes its own tests (see EC_KEY_check_key function)."""
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
                new_number_bytes = (OpenSSL.BN_num_bytes(bn_secret) - 1) * 8 # Decrease the size by 8 bits
                OpenSSL.BN_mask_bits(bn_secret, new_number_bytes) # Truncate
            
            # Compute the public key
            res = OpenSSL.EC_POINT_mul(ec_group, ec_point, bn_secret, 0, 0, bn_ctx)
            if res == 0:
                raise Exception("EC_KEY_new_by_curve_name fails with %s".format(cur))
                        
            # Get public key affine coordinates
            pub_key_x = OpenSSL.BN_new()
            pub_key_y = OpenSSL.BN_new()
            if OpenSSL.EC_POINT_get_affine_coordinates_GFp(ec_group, ec_point, pub_key_x, pub_key_y, 0) == 0:
                raise Exception("EC_POINT_get_affine_coordinates_GFp FAIL ...")
            
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
    
    def _compute_ecc_(self, cur, secret, stagename):
        """Creates a new ECC object"""
        if cur is None:
            return None
        else:
            ho = hashlib.sha512()
            ho.update(secret)
            ho.update("the %s stage ecc secret".format(stagename).encode())
            pubx, puby, priv = self._compute_keypair_(cur, ho.digest())
            return ECC(pubkey_x=pubx, pubkey_y=puby, raw_privkey=priv, curve=cur)
    
    # Extern Methods
    # --------------

    def encrypt(self, stage, data):
        """Encryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None:
            return ecc.encrypt(data, ecc.get_pubkey(), ephemcurve=ecc.get_curve(), ciphername=ciphername)
        else:
            return data
    
    def decrypt(self, stage, cyphertext):
        """Decryption at a certain stage"""
        ecc, ciphername = self._get_ecc_(stage)
        if ecc is not None:
            return ecc.decrypt(cyphertext, ciphername=ciphername)
        else:
            return cyphertext

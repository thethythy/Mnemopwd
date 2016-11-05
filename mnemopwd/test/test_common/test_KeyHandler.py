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

import unittest
import logging
from mnemopwd.common.KeyHandler import KeyHandler


class Test_KeyHandlerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(filename='test/test_common/test_KeyHandler.log')
    
    def setUp(self):
        self.ikey = "this is the key for testing".encode()
        self.foo1 = KeyHandler(self.ikey, cur2='sect409k1', cip2='aes-256-cbc', cur3='sect409k1', cip3='aes-256-cbc')
        self.plaintext1 = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
    def tearDown(self):
        self.foo1 = None

    def test_KeyHandler(self):
        KeyHandler(self.ikey, cur1='secp112r2')
        KeyHandler(self.ikey, cur1='secp128r1')
        KeyHandler(self.ikey, cur1='sect131r2')
        KeyHandler(self.ikey, cur1='secp160k1')
        KeyHandler(self.ikey, cur1='sect239k1')
        KeyHandler(self.ikey, cur1='secp256k1')
        KeyHandler(self.ikey, cur1='secp384r1')
        KeyHandler(self.ikey, cur1='sect409r1')
        KeyHandler(self.ikey, cur1='secp521r1')
        KeyHandler(self.ikey, cur1='sect571r1')
        
    def test_stage1_encrypt_decrypt(self):
        cyphertext = self.foo1.encrypt(0, self.plaintext1)
        self.assertEqual(self.plaintext1, self.foo1.decrypt(0, cyphertext))
        
    def test_stage2_encrypt_decrypt(self):
        cyphertext = self.foo1.encrypt(1, self.plaintext1)
        self.assertEqual(self.plaintext1, self.foo1.decrypt(1, cyphertext))
        
    def test_stage3_encrypt_decrypt(self):
        cyphertext = self.foo1.encrypt(2, self.plaintext1)
        self.assertEqual(self.plaintext1, self.foo1.decrypt(2, cyphertext))
        
    def test_stage12_encrypt_decrypt(self):
        cyphertext = self.foo1.encrypt(0, self.plaintext1)
        cyphertext = self.foo1.encrypt(1, cyphertext)
        cyphertext = self.foo1.decrypt(1, cyphertext)
        self.assertEqual(self.plaintext1, self.foo1.decrypt(0, cyphertext))

if __name__ == '__main__':
    unittest.main()

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

import unittest
import logging
from common.KeyHandler import KeyHandler

class  Test_KeyHandlerTestCase(unittest.TestCase):
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


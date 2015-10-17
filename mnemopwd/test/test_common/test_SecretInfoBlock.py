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
import pickle
from pyelliptic import hash as _hash
from common.SecretInfoBlock import SecretInfoBlock
from common.KeyHandler import KeyHandler

class  SecretInfoBlockTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(filename='test/test_common/test_SecretInfoBlock.log')
        SecretInfoBlockTestCase.ikey = "this is the key for testing".encode()
        SecretInfoBlockTestCase.keyh = KeyHandler(SecretInfoBlockTestCase.ikey, \
                                                  cur2='secp256k1', cip2='aes-128-cbc', \
                                                  cur3='sect283r1', cip3='rc4')
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.nbInfo1 = 1
        self.foo1 = SecretInfoBlock(SecretInfoBlockTestCase.keyh)
        
        # Compute hmac
        state = self.foo1.__dict__.copy()
        del state['keyH']
        state_list = list(state['_infos'].items())
        state_list.append(('_nbInfo', state['_nbInfo']))
        state_list.sort()
        sorted_list =  str(state_list).encode()
        self.hmac1 = _hash.hmac_sha512(SecretInfoBlockTestCase.keyh.ikey, sorted_list)
        
        self.nbInfo2 = 2
        self.foo2 = SecretInfoBlock(SecretInfoBlockTestCase.keyh, self.nbInfo2)
        self.value = "value".encode()

    def tearDown(self):
        self.foo = None
        self.foo2 = None

    def test_InfoUnit(self):
        self.assertEqual(self.foo1.nbInfo, self.nbInfo1)
        self.assertEqual(self.foo2.nbInfo, self.nbInfo2)
        
    def test_setter_infos(self):
        goodref = self.foo1.infos
        self.foo1.infos = dict()
        self.assertEqual(goodref, self.foo1.infos)
    
    def test_deleter_infos(self):
        goodref = self.foo1.infos
        del self.foo1.infos
        self.assertEqual(goodref, self.foo1.infos)
    
    def test_setter_nbInfo(self):
        with self.assertRaises(AssertionError):
            self.foo1.nbInfo = 0
            self.foo1.nbInfo = -10
            self.foo1.nbInfo = "10"
            self.foo1.nbInfo = 1.0
        
        self.foo2.nbInfo += 1
        self.foo2._verify_index_("info3")
        self.foo2["info3"] = self.value
        
        self.foo2.nbInfo = 2
        with self.assertRaises(KeyError):
            self.foo2._verify_index_("info3")
            
    def test_deleter_nbInfo(self):
        del self.foo1.nbInfo
        self.assertEqual(self.foo1.nbInfo, self.nbInfo1)

    def test__getstate__(self):
        state = self.foo1.__getstate__()
        self.assertEqual(state["fingerprint"], self.hmac1)

        self.foo1["info1"] = self.value
        state = self.foo1.__getstate__()
        self.assertNotEqual(state["fingerprint"], self.hmac1)

    def test__setstate__(self):
        state = self.foo1.__getstate__()
        self.foo1.__setstate__(state)
        
        state = {"_infos":{}, "_nbInfo":2, "fingerprint":self.hmac1}
        with self.assertRaises(AssertionError):
            self.foo1.__setstate__(state)
            
        state = {"_infos":{"info1":self.value}, "_nbInfo":1, "fingerprint":self.hmac1}
        with self.assertRaises(AssertionError):
            self.foo1.__setstate__(state)

    def test__verifyindex__(self):
        with self.assertRaises(TypeError):
            self.foo1._verify_index_(10)

        with self.assertRaises(KeyError):
            self.foo1._verify_index_("foo")

        with self.assertRaises(KeyError):
            self.foo1._verify_index_("info")

        self.foo1._verify_index_("info1")

        with self.assertRaises(KeyError):
            self.foo1._verify_index_("info2")
        
        self.foo1.nbInfo += 1
        self.foo1._verify_index_("info2")
        
        self.foo2._verify_index_("info2")

    def test__getitem__(self):
        with self.assertRaises(TypeError):
            info = self.foo1[10]

        with self.assertRaises(KeyError):
            info = self.foo1["foo"]

        with self.assertRaises(KeyError):
            info = self.foo1["info"]

        with self.assertRaises(KeyError):
            info = self.foo1["info1"]

        self.foo1["info1"] = self.value
        self.assertEqual(self.value, self.foo1["info1"])

        self.foo1.nbInfo += 1
        self.foo1["info2"] = self.value
        self.assertEqual(self.value, self.foo1["info2"])

    def test__setitem__(self):
        self.foo1["info1"] = self.value
        self.assertEqual(self.value, self.foo1["info1"])

        with self.assertRaises(KeyError):
            self.foo1["info2"] = self.value

        self.foo1.nbInfo += 1
        self.foo1["info2"] = self.value
        self.assertEqual(self.value, self.foo1["info2"])

    def test__delitem__(self):
        with self.assertRaises(KeyError):
            del self.foo1["info1"]

        self.foo1["info1"] = self.value
        del self.foo1["info1"]
        with self.assertRaises(KeyError):
            del self.foo1["info1"]

    def test__contains__(self):
        self.assertFalse(self.value in self.foo1)
        self.foo1["info1"] = self.value
        self.assertTrue(self.value in self.foo1)

    def test__len__(self):
        self.assertEqual(len(self.foo1), 0)
        self.foo1["info1"] = self.value
        self.assertEqual(len(self.foo1), 1)
        
        self.foo1.infos["info2"] = self.value
        with self.assertRaises(AssertionError):
            len(self.foo1)

if __name__ == '__main__':
    unittest.main()


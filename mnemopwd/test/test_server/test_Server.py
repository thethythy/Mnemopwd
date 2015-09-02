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
import threading
import socket
import ssl
import time
from server.server import Server

class Test_Server_Client(threading.Thread):
    def __init__(self, host, port, test):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.test = test
        
    def run(self):
        try:
            time.sleep(1)
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.options |= ssl.OP_NO_SSLv2 # SSL v2 not allowed
            context.options |= ssl.OP_NO_SSLv3 # SSL v3 not allowed
            context.set_ciphers("AECDH-AES256-SHA")
            context.verify_mode = ssl.CERT_NONE
            connect = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.host)
            connect.connect((self.host, self.port))
            
            (cipher, version, bits) = connect.cipher()
            self.test.assertEqual(cipher, 'AECDH-AES256-SHA')
            self.test.assertEqual(bits, 256)
            print("Connection with the server")
        
        finally:
            time.sleep(1)
            connect.close()
            print("Disconnection with the server")
        
class  Test_ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.host = "127.0.0.1"
        self.port = 25600

    def tearDown(self):
        pass
                    
    def test_Server(self):
        Test_Server_Client(self.host, self.port, self).start()
        print("Use Ctrl+C to finish the test")
        try:
            s = Server(self.host, self.port)
            s.start()
        except KeyboardInterrupt:
            pass
        finally:
            s.close()
        
if __name__ == '__main__':
    unittest.main()

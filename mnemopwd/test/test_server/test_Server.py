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
from pyelliptic import ECC
from pyelliptic.hash import pbkdf2

class Test_Server_Client_S0(threading.Thread):
    def __init__(self, host, port, test, number):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.test = test
        self.number = number
        
    def connect_to_server(self):
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
        print("Client", self.number, ": connection with the server")
        return connect
    
    def state_S0(self, connect):
        message = connect.recv(1024)
        protocol_cd = message[:10]
        protocol_data = message[11:]
        self.test.assertEqual(protocol_cd, b'KEYSHARING')
        self.ephecc = ECC(pubkey=protocol_data)
        self.test.assertEqual(protocol_data, self.ephecc.get_pubkey())
        
    def run(self):
        try:
            connect = self.connect_to_server()
            # State 0
            self.state_S0(connect)
        finally:
            time.sleep(1)
            connect.close()
            print("Client", self.number, ": disconnection with the server")
       
class Test_Server_Client_S11(Test_Server_Client_S0):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S0.__init__(self,host,port,test,number)
        self.password = 'This is the test password'.encode()
        self.login = 'This is the client S11 login'.encode()
        
    def state_S11(self, connect):
        salt, ms = pbkdf2(self.password, salt=self.login)
        ems = self.ephecc.encrypt(ms, pubkey=self.ephecc.get_pubkey())
        elogin = self.ephecc.encrypt(self.login, pubkey=self.ephecc.get_pubkey())        
        connect.send(b'CREATION;' + ems + b';' + elogin)
        
    def run(self):
        try:
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 11
            self.state_S11(connect)
        finally:
            time.sleep(1)
            connect.close()
            print("Client", self.number, ": disconnection with the server")
        
class  Test_ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.host = "127.0.0.1"
        self.port = 25600
        self.path = '/tmp/'

    def tearDown(self):
        pass
                    
    def test_Server(self):
        Test_Server_Client_S0(self.host, self.port, self, 1).start()
        Test_Server_Client_S11(self.host, self.port, self, 2).start()
        print("Use Ctrl+C to finish the test")
        try:
            s = Server(self.host, self.port, self.path)
            s.start()
        except KeyboardInterrupt:
            pass
        finally:
            s.close()
        
if __name__ == '__main__':
    unittest.main()

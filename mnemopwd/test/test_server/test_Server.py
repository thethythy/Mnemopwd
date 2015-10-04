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
from pathlib import Path
from server.server import Server
from server.util.Configuration import Configuration
from pyelliptic import ECC
from pyelliptic import OpenSSL
from pyelliptic import Cipher
from pyelliptic import pbkdf2
from pyelliptic import hmac_sha512
from pyelliptic import hmac_sha256
import hashlib

# -----------------------------------------------------------------------------
# Test S0

class Test_Server_Client_S0(threading.Thread):
    def __init__(self, host, port, test, number):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.test = test
        self.number = number
        
    def connect_to_server(self):
        time.sleep(1) # Waiting server
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
        #print("Client", self.number, "state_S0 : starting")
        message = connect.recv(1024)
        #print("Client", self.number, "state_S0 : receiving")
        
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
            connect.close()
            print("Client", self.number, ": disconnection with the server")

# -----------------------------------------------------------------------------
# Test S1            
            
class Test_Server_Client_S1_OK(Test_Server_Client_S0):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S0.__init__(self,host,port,test,number)
        self.password = 'This is the test password'.encode()
        self.login = 'This is the client S21 login'.encode()

    def state_S1S_begin(self, connect):
        salt, ms = pbkdf2(self.password, salt=self.login)
        self.ms = ms
        ems = self.ephecc.encrypt(self.ms, pubkey=self.ephecc.get_pubkey())
        connect.send(b'SESSION;' + ems)

    def state_S1S_end(self, connect):
        message = connect.recv(1024)
        protocol_cd = message[:10]
        blocksize = OpenSSL.get_cipher('aes-256-cbc').get_blocksize()
        self.iv = message[11:11+blocksize]
        self.esession = message[12+blocksize:]        
        self.test.assertEqual(protocol_cd, b'CHALLENGER')        
    
    def get_echallenge(self, var, bug=False):
        if bug:
            challenge = hmac_sha256(self.ms, self.session + b'BUG')
        else:
            challenge = hmac_sha256(self.ms, self.session + var)
        return self.ephecc.encrypt(challenge, pubkey=self.ephecc.get_pubkey())
    
    def state_S1C_begin(self, connect):
        ctx = Cipher(self.ms, self.iv, 0, 'aes-256-cbc')
        self.session = ctx.ciphering(self.esession)        
        echallenge = self.get_echallenge(b'S1.12')
        
        connect.send(b'CHALLENGEA;' + echallenge)
        
    def state_S1C_end(self, connect):
        message = connect.recv(1024)
        protocol_cd = message[:2]
        self.test.assertEqual(protocol_cd, b'OK')
    
    def run(self):
        try:
            time.sleep(3) # Waiting previous test
            connect = self.connect_to_server()
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")     

class Test_Server_Client_S1_KO(Test_Server_Client_S1_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S1_OK.__init__(self,host,port,test,number)

    def state_S1C_begin(self, connect):
        ctx = Cipher(self.ms, self.iv, 0, 'aes-256-cbc')
        self.session = ctx.ciphering(self.esession)
        echallenge = self.get_echallenge(b'S1.12', bug=True)        
        connect.send(b'CHALLENGEA;' + echallenge)
        
    def state_S1C_end(self, connect):
        message = connect.recv(1024)
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'challenge rejected')
    
    def run(self):
        try:
            connect = self.connect_to_server()
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

# -----------------------------------------------------------------------------
# Test S21

class Test_Server_Client_S21_OK(Test_Server_Client_S1_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S1_OK.__init__(self,host,port,test,number)
        
    def state_S21_Begin(self, connect, bug=False):        
        echallenge = self.get_echallenge(b'S21.7')     
        
        ho = hashlib.sha256()
        if bug :
            ho.update(hmac_sha512(self.ms, self.ms + self.login + b'bug')) # Wrong id
        else:
            ho.update(hmac_sha512(self.ms, self.ms + self.login)) # Good id
        id = ho.digest()
        eid = self.ephecc.encrypt(id, pubkey=self.ephecc.get_pubkey())
        
        elogin = self.ephecc.encrypt(self.login, pubkey=self.ephecc.get_pubkey())
        
        connect.send(echallenge + b';LOGIN;' + eid + b';' + elogin)

    def state_S21_OK(self, connect):
        #print("Client", self.number, "state_S21_KO : starting")    
        message = connect.recv(1024)
        #print("Client", self.number, "state_S21_KO : receiving")
        
        protocol_cd = message[:2]
        self.test.assertEqual(protocol_cd, b'OK')
        
    def run(self):
        try:
            time.sleep(3) # Waiting previous test
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 21
            self.state_S21_Begin(connect)
            self.state_S21_OK(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

class Test_Server_Client_S21_KO_ID(Test_Server_Client_S21_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S1_OK.__init__(self,host,port,test,number)
                
    def state_S21_KO(self, connect):
        #print("Client", self.number, "state_S21_KO : starting")    
        message = connect.recv(1024)
        #print("Client", self.number, "state_S21_KO : receiving")
        
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'incorrect id') 
        
    def run(self):
        try:
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 21
            self.state_S21_Begin(connect, bug=True)
            self.state_S21_KO(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

class Test_Server_Client_S21_KO_COUNT(Test_Server_Client_S21_KO_ID):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S21_KO_ID.__init__(self,host,port,test,number)
                                
    def state_S21_KO(self, connect):
        #print("Client", self.number, "state_S22_KO : starting")
        message = connect.recv(1024)
        #print("Client", self.number, "state_S22_KO : receiving")
        
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'count does not exist')
        
    def run(self):
        try:
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 21
            self.state_S21_Begin(connect)
            self.state_S21_KO(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server") 

# -----------------------------------------------------------------------------
# Test S22

class Test_Server_Client_S22_OK(Test_Server_Client_S1_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S1_OK.__init__(self,host,port,test,number)
        
    def state_S22_Begin(self, connect, bug=False):        
        echallenge = self.get_echallenge(b'S22.7')
        
        ho = hashlib.sha256()
        if bug :
            ho.update(hmac_sha512(self.ms, self.ms + self.login + b'bug')) # Wrong id
        else:
            ho.update(hmac_sha512(self.ms, self.ms + self.login)) # Good id
        id = ho.digest()
        eid = self.ephecc.encrypt(id, pubkey=self.ephecc.get_pubkey())

        elogin = self.ephecc.encrypt(self.login, pubkey=self.ephecc.get_pubkey())        
        
        connect.send(echallenge + b';CREATION;' + eid + b';' + elogin)
                
    def state_S22_OK(self, connect):        
        #print("Client", self.number, "state_S22 : starting")
        message = connect.recv(1024)
        #print("Client", self.number, "state_S22 : receiving")
        
        protocol_cd = message[:5]
        self.test.assertEqual(protocol_cd, b'OK')
        
    def run(self):
        try:
            time.sleep(2) # Waiting previous test
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 22
            self.state_S22_Begin(connect)
            self.state_S22_OK(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

class Test_Server_Client_S22_KO_ID(Test_Server_Client_S22_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S22_OK.__init__(self,host,port,test,number)
                
    def state_S22_KO(self, connect):        
        #print("Client", self.number, "state_S22 : starting")
        message = connect.recv(1024)
        #print("Client", self.number, "state_S22 : receiving")
        
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'incorrect id')
        
    def run(self):
        try:
            time.sleep(3) # Waiting previous test
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 22
            self.state_S22_Begin(connect, bug=True)
            self.state_S22_KO(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

class Test_Server_Client_S22_KO_COUNT(Test_Server_Client_S22_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S22_OK.__init__(self,host,port,test,number)
                
    def state_S22_KO(self, connect):        
        #print("Client", self.number, "state_S22 : starting")
        message = connect.recv(1024)
        #print("Client", self.number, "state_S22 : receiving")
        
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'count already used')
        
    def run(self):
        try:
            time.sleep(3) # Waiting previous test
            connect = self.connect_to_server() 
            # State 0
            self.state_S0(connect)
            # State 1S
            self.state_S1S_begin(connect)
            self.state_S1S_end(connect)
            # State 1C
            self.state_S1C_begin(connect)
            self.state_S1C_end(connect)
            # State 22
            self.state_S22_Begin(connect)
            self.state_S22_KO(connect)
        finally:
            connect.close()
            print("Client", self.number, ": disconnection with the server")

class Test_ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.path = 'test/data'
        for child in Path(self.path).iterdir(): Path(child).unlink()

    def tearDown(self):
        pass
                    
    def test_Server(self):
        Test_Server_Client_S0(Configuration.host, Configuration.port, self, 1).start()
        Test_Server_Client_S1_OK(Configuration.host, Configuration.port, self, 2).start()
        Test_Server_Client_S1_KO(Configuration.host, Configuration.port, self, 3).start()
        Test_Server_Client_S21_KO_ID(Configuration.host, Configuration.port, self, 4).start()
        Test_Server_Client_S21_KO_COUNT(Configuration.host, Configuration.port, self, 5).start()
        
        # Begin after 2 secondes
        Test_Server_Client_S22_OK(Configuration.host, Configuration.port, self, 6).start()        
        
        # Begin after 3 secondes
        Test_Server_Client_S22_KO_ID(Configuration.host, Configuration.port, self, 7).start()
        Test_Server_Client_S22_KO_COUNT(Configuration.host, Configuration.port, self, 8).start()
        Test_Server_Client_S21_OK(Configuration.host, Configuration.port, self, 9).start()

        print("Use Ctrl+C to finish the test")
        try:
            Configuration.dbpath = self.path
            s = Server()
            s.start()
        except KeyboardInterrupt:
            pass
        finally:
            s.close()
        
if __name__ == '__main__':
    unittest.main()

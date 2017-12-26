# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
import threading
import subprocess
import socket
import ssl
import time
import os
from pathlib import Path
from mnemopwd.server.server import Server
from mnemopwd.server.util.Configuration import Configuration
from mnemopwd.pyelliptic import ECC
from mnemopwd.pyelliptic import Cipher
from mnemopwd.pyelliptic import pbkdf2
from mnemopwd.pyelliptic import hmac_sha256

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
        
        protocol = getattr(ssl, "PROTOCOL_TLSv1_2", False)
        if not protocol: protocol = getattr(ssl, "PROTOCOL_TLSv1_1", False)
        if not protocol: protocol = getattr(ssl, "PROTOCOL_TLSv1", False)
        if not protocol: protocol = getattr(ssl, "PROTOCOL_SSLv23", False)
        context = ssl.SSLContext(protocol)
        context.verify_mode = ssl.CERT_OPTIONAL
        context.check_hostname = False
        context.options |= ssl.OP_NO_SSLv2 # SSL v2 not allowed
        context.options |= ssl.OP_NO_SSLv3 # SSL v3 not allowed
        context.load_verify_locations(cafile=Configuration.certfile)
        connect = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        connect.connect((self.host, self.port))
        
        self.sockname = connect.getsockname()
        print("Client", self.number, self.sockname, ": connection with the server")
        return connect
    
    def state_S0(self, connect):
        message = connect.recv(4096)
        
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
            print("Client", self.number, self.sockname, ": disconnection with the server")

# -----------------------------------------------------------------------------
# Test S1


class Test_Server_Client_S1_OK(Test_Server_Client_S0):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S0.__init__(self,host,port,test,number)
        self.password = 'This is the test password'.encode()
        self.login = 'This is the client S21 login'.encode()

    def state_S1S_begin(self, connect):
        salt, ms = pbkdf2(self.password, salt=self.login, hfunc='SHA1')
        self.ms = ms
        ems = self.ephecc.encrypt(self.ms, pubkey=self.ephecc.get_pubkey())

        nonce = (os.urandom(32))  # Random nonce (32 bytes)
        cipher = Cipher(ms, Cipher.gen_IV('aes-256-cbc'), 1, 'aes-256-cbc')
        self.session = cipher.ciphering(nonce)[:16]  # Compute session number (16 bytes)
        esession = self.ephecc.encrypt(self.session, pubkey=self.ephecc.get_pubkey())
        len_esession = str(len(esession)).encode()

        connect.send(b'SESSION;' + len_esession + b';' + esession + b';' + ems)

    def state_S1S_end(self, connect):
        message = connect.recv(4096)
        protocol_cd = message[:10]
        self.test.assertEqual(protocol_cd, b'CHALLENGER')
    
    def get_echallenge(self, var, bug=False):
        if bug:
            challenge = hmac_sha256(self.ms, self.session + b'BUG')
        else:
            challenge = hmac_sha256(self.ms, self.session + var)
        return self.ephecc.encrypt(challenge, pubkey=self.ephecc.get_pubkey())
    
    def state_S1C_begin(self, connect):
        echallenge = self.get_echallenge(b'S1.13')
        connect.send(b'CHALLENGEA;' + echallenge)
        
    def state_S1C_end(self, connect):
        message = connect.recv(4096)
        protocol_cd = message[:2]
        self.test.assertEqual(protocol_cd, b'OK')
    
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
            print("Client", self.number, self.sockname, ": disconnection with the server")


class Test_Server_Client_S1_KO(Test_Server_Client_S1_OK):
    def __init__(self, host, port, test, number):
        Test_Server_Client_S1_OK.__init__(self,host,port,test,number)

    def state_S1C_begin(self, connect):
        echallenge = self.get_echallenge(b'S1.13', bug=True)
        connect.send(b'CHALLENGEA;' + echallenge)
        
    def state_S1C_end(self, connect):
        message = connect.recv(4096)
        protocol_cd = message[:5]
        protocol_data = message[6:]
        self.test.assertEqual(protocol_cd, b'ERROR')
        self.test.assertEqual(protocol_data, b'application protocol error')
    
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
            print("Client", self.number, self.sockname, ": disconnection with the server")
            print("Use Ctrl+c to finish the test")

# -----------------------------------------------------------------------------


class Test_ServerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.path = 'mnemopwd/test/data'
        self.requestfile = self.path + '/testreq'
        self.keyfile = self.path + '/testkey'
        self.certfile = self.path + '/testcert'
        # Generate a new certfile
        if Path(self.path + '/testcert').exists() :
            Path(self.path + '/testcert').unlink()
        with subprocess.Popen(['openssl', 'req', '-x509',  '-in',  self.requestfile, '-key', self.keyfile, '-out', self.certfile], stdout=subprocess.PIPE) as proc:
            print(proc.stdout.read())

    def test_Server(self):
        Configuration.certfile = self.certfile
        Configuration.keyfile = self.keyfile
        Test_Server_Client_S0(Configuration.host, Configuration.port, self, 1).start()
        Test_Server_Client_S1_OK(Configuration.host, Configuration.port, self, 2).start()
        Test_Server_Client_S1_KO(Configuration.host, Configuration.port, self, 3).start()
        
        try:
            Configuration.dbpath = self.path
            Configuration.search_mode = 'all'
            Configuration.loglevel = 'DEBUG'
            Configuration.logfile = self.path + '/mnemopwds.log'
            Server().start()
        except KeyboardInterrupt:
            pass
        
if __name__ == '__main__':
    unittest.main()

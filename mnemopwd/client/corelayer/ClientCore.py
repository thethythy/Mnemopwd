# -*- coding: utf-8 -*-

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
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

import logging
import asyncio
import socket
import ssl
import time
import concurrent.futures
import functools
from client.util.Configuration import Configuration
from client.util.funcutils import Subject
from client.corelayer.protocol.ProtocolHandler import ProtocolHandler

"""
Client part of Mnemopwd application.
"""

class ClientCore(Subject):
    """
    Client module of the application
    
    Attribut(s):
    - loop: an i/o asynchronous loop (see the official asyncio module)
    - transport: a SSL/TLS asynchronous socket (see the official ssl module)
    - protocol: a communication handler (see the official asyncio module)
    
    Method(s):
    - open: open a new connection to the server
    - close: close the connection
    - start: start the domain layer
    - stop: close the domain loop
    - setCredentials: set login/password then start S1 state
    """
    
    # Intern methods
    
    def __init__(self):
        """Initialization"""
        Subject.__init__(self)
        
        # Create an i/o asynchronous loop
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(Configuration.loglevel == 'DEBUG')
        logging.basicConfig(level=Configuration.loglevel)
        
        # Create and set an executor
        executor = concurrent.futures.ThreadPoolExecutor(Configuration.poolsize)
        self.loop.set_default_executor(executor)
        
        # Create a SSL context
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.options |= ssl.OP_NO_SSLv2 # SSL v2 not allowed
        self.context.options |= ssl.OP_NO_SSLv3 # SSL v3 not allowed
        self.context.verify_mode = ssl.CERT_OPTIONAL # Server certificat is optional
        self.context.check_hostname = False # Don't check hostname because of shared certificat
        if Configuration.certfile != 'None' :
            self.context.load_verify_locations(cafile=Configuration.certfile) # Load certificat
        else:
            self.context.set_ciphers("AECDH-AES256-SHA") # Cipher suite to use
        
        if Configuration.action == 'status':
            self.open() # Try to open a connection to server
            print("the server seems running at " + str(self.transport.get_extra_info('peername')))
        
    # Extern methods
    
    def open(self):
        """Open a new connection to the server"""
        # Create an asynchronous SSL socket
        coro = self.loop.create_connection(lambda: ProtocolHandler(self), \
                                           Configuration.server, Configuration.port, \
                                           family=socket.AF_INET, ssl=self.context)
        # Try to open SSL socket
        try:
            if not self.loop.is_running():
                self.transport, self.protocol = self.loop.run_until_complete(coro)
            else:
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                self.transport, self.protocol = future.result(1)
                time.sleep(0.5)
                
        except ConnectionRefusedError as e:
            print(e)
            print("The server seems not running. Verify ip and port number.")
            raise
        except ssl.SSLError as e:
            print(e)
            print("There is a problem with the certificat.")
            raise
        except Exception as e:
            print(e)
            raise
    
    def close(self):
        """Close the connection with the server"""
        self.loop.call_soon_threadsafe(self.transport.close) # Ask to close connection
    
    def start(self):
        """Start the main loop"""
        self.update('connection.state', 'Please start a connection')
        self.loop.run_forever() # Run until the end of the loop
        self.loop.close()       # Close the main loop
        
    def stop(self):
        """Close the connection to the server then stop the main loop"""
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop) # Ask to stop the main loop
        else:
            self.transport.close()
            self.loop.close()
            
    def setCredentials(self, login, password):
        """Store login and password then start state S1"""
        self.protocol.login = login.encode()
        self.protocol.password = password.encode()
        self.protocol.data_received(None)


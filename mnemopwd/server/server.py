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

import logging
import asyncio
import socket
import ssl
import concurrent.futures
from server.util.Configuration import Configuration
from server.clients.ClientHandler import ClientHandler

"""
Server part of Mnemopwd application.
Must be run by a script according to the OS of the server node.
"""

class Server:
    """
    Server module of the application
    
    Attribut(s):
    - loop : an i/o asynchronous loop (see the official python asyncio module)
    - server : a SSL/TLS asynchronous socket server (see the official python ssl module)
    
    Method(s):
    - start : start the server
    - stop : stop the server (can be re-started)
    - close : close the server
    """
    
    # Intern methods
    
    def __init__(self):
        """Initialization"""
        logging.basicConfig(filename=Configuration.dbpath + '/mnemopwds.log', \
                            level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', \
                            datefmt='%m/%d/%Y %I:%M:%S')
        logging.info("-----------------------------------------------------------")
        
        # Create a i/o asynchronous loop
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        
        # Create and set an executor
        executor = concurrent.futures.ThreadPoolExecutor(Configuration.poolsize)
        self.loop.set_default_executor(executor)
        
        # Create a SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.options |= ssl.OP_NO_SSLv2 # SSL v2 not allowed
        context.options |= ssl.OP_NO_SSLv3 # SSL v3 not allowed
        context.options |= ssl.OP_SINGLE_ECDH_USE # Change ECDH key at every session
        context.set_ecdh_curve('sect409k1') # Why not ?
        context.set_ciphers('AECDH-AES256-SHA') # Use only ECDH-anon
        context.verify_mode = ssl.CERT_NONE # No client certificat
        
        # Create an asynchronous SSL server
        coro = self.loop.create_server(lambda: ClientHandler(self.loop, Configuration.dbpath), \
                                        Configuration.host, Configuration.port, \
                                        family=socket.AF_INET, ssl=context, \
                                        reuse_address=True)
        self.server = self.loop.run_until_complete(coro)
            
    # Extern methods
    
    def start(self):
        """Start the main loop"""
        logging.info("Server started (or restarted) at {}".format(self.server.sockets[0].getsockname()))
        self.loop.run_forever()
        
    def stop(self):
        """Stop temporarily the main loop. After this method, call start method to re-start"""
        self.loop.stop()
        logging.info("Server in standby")
        
    def close(self):
        """Close the server and the main loop.
        For normal closing do not call after the stop method but after the start method."""
        self.server.close()
        if self.loop.is_running():
            self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()
        logging.info("Server closed")

if __name__ == "__main__":
    # TODO : daemon
    Configuration.configure()
    Server().start()
    
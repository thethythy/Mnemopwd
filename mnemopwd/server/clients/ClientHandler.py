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


import asyncio
import logging
import os

from ...pyelliptic import OpenSSL
from .protocol import *
from ...common.KeyHandler import KeyHandler
from ...common.SecretInfoBlock import SecretInfoBlock
from .DBHandler import DBHandler
from .DBAccess import DBAccess

"""
The client connection handler
"""


class ClientHandler(asyncio.Protocol):
    """The client connection handler"""
    
    def __init__(self, loop, path):
        """Initialize the handler"""
        self.dbpath = path  # The path to the database
        self.loop = loop  # The i/o asynchronous loop
        # The protocol states
        self.states = {
            '0': StateS0(), '1S': StateS1S(), '1C': StateS1C(),
            '2': StateS2(), '21': StateS21(), '22': StateS22(),
            '3': StateS3(), '31': StateS31(), '32': StateS32(),
            '33': StateS33(), '34': StateS34(), '35': StateS35(),
            '36': StateS36(), '37': StateS37()
        }

    def connection_made(self, transport):
        """Connection starting : set default protocol state and start it"""
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        cipher = transport.get_extra_info('cipher')
        logging.info('Connection from {} with {}'.format(self.peername, cipher))
                
        # Set the default state and schedule its execution
        self.state = self.states['0']  # State 0 at the beginning
        self.loop.run_in_executor(None, self.state.do, self, None)

    def connection_lost(self, exc):
        """Connection finishing"""
        if exc is None:
            logging.info('Disconnection from {}'.format(self.peername))
        else:
            logging.warning('Lost connection from {}'.format(self.peername))
        self.transport.close()

    def data_received(self, data):
        """Data received"""
        # Future excecution
        self.loop.run_in_executor(None, self.state.do, self, data)

    def exception_handler(self, exc):
        """Exception handler for actions executed by the executor"""
        logging.critical('Closing connection with {} because server detects an error : {}'
                         .format(self.peername, exc))
        self.transport.close()

    def configure_crypto(self, config_demand):
        """Configure cryptographic handler"""
        
        with DBAccess.getLock(self.dbH.database):
            # Control curve and cipher names
            try:
                for i, name in enumerate(config_demand.split(';')):
                    if name != '':
                        if i % 2 == 0: 
                            OpenSSL.get_curve(name)  # Control curve name
                        else: 
                            OpenSSL.get_cipher(name)  # Control cipher name
            except Exception:
                return False

            # Configure crypto handler
            result = 1
            try:
                if self.dbH['config'] != config_demand:
                    # Case 2 : new configuration demand
                    self.dbH['config_tmp'] = config_demand
                    logging.warning('New configuration {} from {}'
                                    .format(config_demand, self.peername))
                    result = 2
                else:
                    # Case 1 : same configuration
                    logging.info('Same configuration {} from {}'
                                 .format(config_demand, self.peername))
        
            except KeyError:
                # Case 1 : no configuration exist 
                self.dbH['config'] = config_demand
                logging.info('First configuration {} from {}'
                             .format(config_demand, self.peername))
        
            except:
                # Unexpected error
                return False

            finally:
                # Configure client with actual cryptographic suite
                config_actual = (self.dbH['config']).split(';')
                self.keyH = KeyHandler(
                    self.ms, cur1=config_actual[0], cip1=config_actual[1],
                    cur2=config_actual[2], cip2=config_actual[3],
                    cur3=config_actual[4], cip3=config_actual[5])
        
        # Return False (wrong configuration) or 1 (same or first) or 2 (new)
        return result
        
    def update_crypto(self):
        """
        Change all secret information with the new cryptographic configuration
        """
        
        with DBAccess.getLock(self.dbH.database):
            try:
                # Create an empty database
                if DBHandler.new(self.dbH.path, self.dbH.filename + '_tmp'):
        
                    # Create new handlers
                    dbH_tmp = DBHandler(
                        self.dbH.path, self.dbH.filename + '_tmp')
                    config_tmp = self.dbH['config_tmp']
                    dbH_tmp['config'] = config_tmp
                    config = config_tmp.split(';')
                    keyH_tmp = KeyHandler(
                        self.ms, cur1=config[0], cip1=config[1],
                        cur2=config[2], cip2=config[3],
                        cur3=config[4], cip3=config[5])
                
                    # Data exchange
                    nbsibs = self.dbH['nbsibs']
                    index = self.dbH['index']
                    if nbsibs > 0:
                    
                        dbH_tmp['nbsibs'] = nbsibs  # Same 'nbsibs' value
                        dbH_tmp['index'] = index    # Same 'index' value
                        
                        for i in range(1, index + 1):  # For all sibs

                            try:
                                # Original secret information block
                                sib = self.dbH[str(i)]
                            except KeyError:
                                continue  # Continue with the next key

                            sib.keyH = self.keyH  # Set actual KeyHandler
                            if sib.nbInfo > 0:
                                # New sib with new KeyHandler
                                sib_tmp = SecretInfoBlock(keyH_tmp, sib.nbInfo)
                                # For all secret information
                                for j in range(1, sib.nbInfo + 1):
                                    # Exchange
                                    sib_tmp['info' + str(j)] = sib['info' + str(j)]
                                    # Verification
                                    assert sib_tmp['info' + str(j)] == sib['info' + str(j)]
                                # Save sib in the new database with same index
                                dbH_tmp[str(i)] = sib_tmp
                                
                    # Delete original database
                    os.unlink(self.dbH.path + '/' + self.dbH.filename + '.db')
                    # Rename temporary database
                    os.rename(self.dbH.path + '/' + self.dbH.filename + '_tmp.db',
                              self.dbH.path + '/' + self.dbH.filename + '.db')
                    # Update handlers of the client handler
                    self.dbH = dbH_tmp
                    self.keyH = keyH_tmp
                
                else:
                    # File system problem? Bad directory? Permission problem?
                    raise Exception()
            
            except:
                # Delete temporary database
                os.unlink(self.dbH.path + '/' + self.dbH.filename + '_tmp.db')
                # Delete new configuration string
                del self.dbH['config_tmp']
                return False
        
        return True

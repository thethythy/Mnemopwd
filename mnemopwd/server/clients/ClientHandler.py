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
from server.clients.protocol import *
from pyelliptic import OpenSSL
from common.KeyHandler import KeyHandler
from common.SecretInfoBlock import SecretInfoBlock
from server.clients.DBHandler import DBHandler

"""
The client connection handler
"""

class ClientHandler(asyncio.Protocol):
    """The client connection handler"""
    
    def __init__(self, loop, path):
        """Initialize the handler"""
        self.dbpath = path # The path to the database
        self.loop = loop # The i/o asynchronous loop
        # The protocol states
        self.states = {'0':StateS0(), '1S':StateS1S(), '1C':StateS1C(), \
                       '2':StateS2(), '21':StateS21(), '22':StateS22(), \
                       '3':StateS3(), '31':StateS31(), '36':StateS36()}

    def connection_made(self, transport):
        """Connection starting : set default protocol state and start it"""
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        cipher = transport.get_extra_info('cipher')
        logging.info('Connection from {} with {}'.format(self.peername,cipher))
                
        # Set the default state and schedule its execution
        self.state = self.states['0'] # State 0 at the beginning
        self.loop.run_in_executor(None, self.state.do, self, None) # Future execution
        
    def connection_lost(self, exc):
        """Connection finishing"""
        if exc is None:
            logging.info('Disconnection from {}'.format(self.peername))
        else:
            logging.warning('Lost connection from {}'.format(self.peername))
        # TODO : nothing to do here ????
        self.transport.close()

    def data_received(self, data):
        """Data received"""
        self.loop.run_in_executor(None, self.state.do, self, data) # Future excecution

    def exception_handler(self, exc):
        """Exception handler for actions executed by the executor"""
        logging.critical('Closing connection with {} because server detects an error : {}'.format(self.peername, exc))
        self.transport.close()
        
    def configure_crypto(self, config_demand):
        """Configure cryptographic handler"""
        
        # Control curve and cipher names
        try:
            for i, name in enumerate(config_demand.split(';')) :
                if name != '' and i % 2 == 0: 
                    OpenSSL.get_curve(name) # Control curve name
                elif name != '': 
                    OpenSSL.get_cipher(name) # Control cipher name
        except:
            return False
        
        # Configure crypto handler
        result = 1
        try:
            if self.dbH['config'] != config_demand :
                # Case 2 : new configuration demand
                self.dbH['config_tmp'] = config_demand
                logging.warning('New configuration {} from {}'.format(config_demand, self.peername))
                result = 2
            else:
                # Case 1 : same configuration
                logging.info('Same configuration {} from {}'.format(config_demand, self.peername))
        
        except KeyError:
            # Case 1 : no configuration exist 
            self.dbH['config'] = config_demand
            logging.info('First configuration {} from {}'.format(config_demand, self.peername))
        
        except:
            # Unexpected error
            return False
        
        finally:
            # Configure client with actual cryptographic suite
            config_actual = (self.dbH['config']).split(';')
            self.keyH = KeyHandler(self.ms, cur1=config_actual[0], cip1=config_actual[1], \
                                            cur2=config_actual[2], cip2=config_actual[3], \
                                            cur3=config_actual[4], cip3=config_actual[5])
        # Return False (wrong configuration) or 1 (same or first) or 2 (new)
        return result
        
    def update_crypto(self):
        """Change all secret informations with the new cryptographic configuration"""
        
        try :
        
            # Create an empty database
            if DBHandler.new(self.dbH.path, self.dbH.filename + '_tmp') :
        
                # Create new handlers
                dbhandler_tmp = DBHandler(self.dbH.path, self.dbH.filename + '_tmp')
                config_tmp = self.dbH['config_tmp']
                dbhandler_tmp['config'] = config_tmp
                config = config_tmp.split(';')
                keyhandler_tmp = KeyHandler(self.ms, cur1=config[0], cip1=config[1], \
                                                     cur2=config[2], cip2=config[3], \
                                                     cur3=config[4], cip3=config[5])
            
                print(self.dbH['nb_sibs'])
            
                # Data exchange
                nb_sibs = self.dbH['nb_sibs']
                if nb_sibs > 0 :
                    for i in range(1, nb_sibs + 1) :
                        sib = self.dbH[str(i)]    # Original secret information block
                        sib.keyH = self.keyH      # Set actual keyhandler
                        if sib.nbInfo > 0 :
                            sib_tmp = SecretInfoBlock(keyhandler_tmp, sib.nbInfo) # New sib
                            for j in range(1, sib.nbInfo + 1) : # For all sib in original database
                                print(sib['info' + str(j)])
                                sib_tmp['info' + str(j)] = sib['info' + str(j)] # Exchange
                                assert sib_tmp['info' + str(j)] == sib['info' + str(j)] # Verification
                            dbhandler_tmp.add_data(sib_tmp) # Store new sib in the new database
                            
                # Delete original database
                os.unlink(self.dbH.path + '/' + self.dbH.filename + '.db')
                # Rename temporary database
                os.rename(self.dbH.path + '/' + self.dbH.filename + '_tmp.db', \
                          self.dbH.path + '/' + self.dbH.filename + '.db')
                # Update handlers of the client handler
                self.dbH = dbhandler_tmp
                self.keyH = keyhandler_tmp
                
            else:
                raise Exception() # Not enough space left ? bad directory ? permission problem ?
            
        except:
            # Delete temporary database
            os.unlink(self.dbH.path + '/' + self.dbH.filename + '_tmp.db')
            # Delete new configuration string
            del self.dbH['config_tmp']
            return False
            
        return True
        
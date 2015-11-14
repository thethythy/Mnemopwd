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

"""
State S34 : Deletion
"""

from server.util.funcutils import singleton
from server.clients.protocol import StateSCC
from server.clients.DBHandler import DBHandler

@singleton
class StateS34(StateSCC):
    """State S34 : Deletion"""
        
    def do(self, client, data):
        """Action of the state S34: delete a user account"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S34.7') :
            
                # Test for S34 command
                is_cd_S34 = data[170:178] == b"DELETION"
                if not is_cd_S34 : raise Exception('protocol error')
                
                eid = data[179:348] # id encrypted
                elogin = data[349:] # Login encrypted 
                
                # Compute client id
                login = client.ephecc.decrypt(elogin)
                id = self.compute_client_id(client.ms, login)
                 
                # Get id from client
                id_from_client = client.ephecc.decrypt(eid)
                
                # If ids are not equal
                if id != id_from_client :
                    message = b'ERROR;' + b'incorrect id'
                    client.loop.call_soon_threadsafe(client.transport.write, message)
                    raise Exception('incorrect id')
                
                # Test if login exists
                filename = self.compute_client_filename(id, client.ms, login)
                exist = DBHandler.exist(client.dbpath, filename)
                
                # If login is unknown
                if not exist :
                    message = b'ERROR;' + b'user account does not exist'
                    client.loop.call_soon_threadsafe(client.transport.write, message)
                    raise Exception('user account does not exist')
                    
                # If login is OK try to delete database file
                result = DBHandler.delete(client.dbpath, filename)
                    
                # If database file has been deleted close connection with client
                if result:
                    client.loop.call_soon_threadsafe(client.transport.write, b'OK')
                    client.loop.call_soon_threadsafe(client.transport.close)
                
                # If deletion has failed for some reason
                else:
                    message = b'ERROR;' + b'deletion rejected'
                    client.loop.call_soon_threadsafe(client.transport.write, message)
                    raise Exception('deletion rejected')
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

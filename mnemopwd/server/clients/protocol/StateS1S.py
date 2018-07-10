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


"""
State S1S : Session
"""

from ...util.funcutils import singleton


@singleton
class StateS1S:
    """State S1S : Session"""
        
    def do(self, client, data):
        """Action of the state S1S: get master secret and session number from
        client and do a challenge request"""
        
        try:

            # Test for S1S command
            is_cd_S1S = data[:7] == b"SESSION"
            if not is_cd_S1S:
                raise Exception('S1S protocol error')

            tab_data = data[8:].split(b';', maxsplit=1)  # Split in two
            len_esession = int((tab_data[0]).decode())  # Get length of esession

            esession = tab_data[1][:len_esession]  # Session number encrypted
            session = client.ephecc.decrypt(esession)  # Decrypt session number

            ems = tab_data[1][len_esession+1:]  # Master secret encrypted
            ms = client.ephecc.decrypt(ems)  # Decrypt master secret

            # Send challenge request
            message = b'CHALLENGER'
            client.loop.call_soon_threadsafe(client.transport.write, message)
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
            
        else:
            client.ms = ms  # Store master secret
            client.session = session  # Store session number
            client.state = client.states['1C']  # Next state

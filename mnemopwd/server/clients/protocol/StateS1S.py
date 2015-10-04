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

"""
State S1S : Session
"""

from server.util.funcutils import singleton
from pyelliptic import Cipher

@singleton
class StateS1S():
    """State S1S : Session"""
        
    def do(self, client, data):
        """Action of the state S1S: establish a session number and a challenge request"""
        try:

            # Test for S1S command
            is_cd_S1S = data[:7] == b"SESSION"
            if not is_cd_S1S : raise Exception('protocol error')
                
            ems = data[8:209] # Master secret encrypted
            ms = client.ephecc.decrypt(ems) # Decrypt master secret
            
            session = b'123' # Random session number TODO
            
            iv = Cipher.gen_IV('aes-256-cbc') # TODO configuration value            
            ctx = Cipher(ms, iv, 1, 'aes-256-cbc')
            esession = ctx.ciphering(session) # Encrypt session number
            
            # Send challenge request
            client.transport.write(b'CHALLENGER;' + iv + b';' + esession)
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
            
        else:
            client.ms = ms # Store master secret
            client.session = session # Store session number
            client.state = client.states['1C'] # Next state


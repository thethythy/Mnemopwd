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
State S1C : Challenge
"""

from server.util.funcutils import singleton
from pyelliptic import hmac_sha256

@singleton
class StateS1C():
    """State S1C : control challenge answer"""
        
    def do(self, client, data):
        """Action of the state S1C: control challenge answer"""
        try:

            # Test for S1C command
            is_cd_S1C = data[:10] == b"CHALLENGEA"
            if not is_cd_S1C : raise Exception('protocol error')
              
            echallenge = data[11:] # Encrypted challenge
            challenge = client.ephecc.decrypt(echallenge) # Decrypting challenge
            
            # Compute challenge
            challenge_bis = hmac_sha256(client.ms, client.session + b'S1.12')
            
            if challenge == challenge_bis :
                client.transport.write(b'OK') # Send challenge accepted
            else:
                client.transport.write(b'ERROR;' + b"challenge rejected") # Send challenge rejected
                raise Exception("challenge rejected")
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
            
        else:
            client.state = client.states['2'] # Next state

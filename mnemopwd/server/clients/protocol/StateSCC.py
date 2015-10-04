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
State SCC : Challenge Controller
"""

from pyelliptic import hmac_sha256

class StateSCC():
    """Challenge controller"""
    
    def control_challenge(self, client, data, var):
        """Action of the state SCC: control the challenge answer"""
        try:
              
            echallenge = data[:169] # Encrypted challenge
            challenge = client.ephecc.decrypt(echallenge) # Decrypting challenge
            
            # Compute challenge
            challenge_bis = hmac_sha256(client.ms, client.session + var)
            
            if challenge != challenge_bis :
                client.transport.write(b'ERROR;' + b"challenge rejected") # Send challenge rejected
                raise Exception("challenge rejected")
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
            return False
        
        else:
            return True


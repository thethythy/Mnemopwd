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
State SO : KeySharing
"""

from server.util.funcutils import singleton
from server.clients.protocol import ProtocolState
from pyelliptic import ECC

@singleton
class StateS0():
    """State S0 : KeySharing"""
    
    #def __init__(self, client_handler):
    #    """Initialize object"""
    #    ProtocolState.__init__(self, client_handler)
        
    def do(self, client, data):
        """Action of the state S0: send an ephemeral server public key"""
        try:
            ephecc = ECC() # Create an ephemeral keypair
            client.ephecc = ephecc # Store it in the client
            message = b'KEYSHARING;' + ephecc.get_pubkey() # The message to send            
            client.transport.write(message) # Send the message
            
            # raise Exception("Test exception in StateS0") # TODO
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
        else:
            # Next state
            client.state = client.states['1']

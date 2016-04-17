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

import asyncio
from client.corelayer.protocol import *

"""
Handler of the secure protocol connection with the server
"""

class ProtocolHandler(asyncio.Protocol):
    """
    The secure protocol handler in communication with the server.
    The first state is S0. The state objects are responsible of choosing the next state. 
    
    Attribut(s):
    - core: the ClientCore instance
    - loop: the asyncio loop
    - states: sequence of state objects
    - state: the actual state (set in connection_made and changed by state objects)
    - transport: the SSL socket
    - password: the client password (set by the UI)
    - login: the client login (set by the UI)
    - ephecc: the ephemeral server public key (set by S0 state)
    - ms: the client master secret (set by S1S state)
    - session: the client session number (set by S1CR state)

    Method(s):
    - connection_made: method called when the connection with the server is made
    - data_received: method called each time a new data is received
    - connection_lost: method called when the connection is lost or closed
    - exception_handler: method called when an exception is raised by a state object
    - notify: notify ClientCore a property has changed
    """

    def __init__(self, core):
        self.core = core
        self.loop = core.loop
        self.password = self.login = 'None'
        # The protocol states
        self.states = {'0':StateS0(),
                       '1S':StateS1S(), '1CR':StateS1CR(), '1CA':StateS1CA(),
                       '21R':StateS21R(), '21A':StateS21A(),
                       '22R':StateS22R(), '22A':StateS22A()}

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        self.state = self.states['0'] # State 0 at the beginning

    def data_received(self, data):
        self.loop.run_in_executor(None, self.state.do, self, data) # Future excecution

    def connection_lost(self, exc):
        if exc is None:
            self.notify("connection.state.logout", "Connection closed")
        else:
            self.notify('connection.state', str(exc).capitalize())
        self.transport.close()
        
    def exception_handler(self, exc):
        """Exception handler for actions executed by the executor"""
        self.notify('connection.state', str(exc).capitalize())
        self.transport.close()
        
    def notify(self, property, value):
        """Notify ClientCore a property has changed"""
        self.core.update(property, value)

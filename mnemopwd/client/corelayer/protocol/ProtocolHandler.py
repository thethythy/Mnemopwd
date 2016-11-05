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
import threading

from . import *
from ...util.Configuration import Configuration
from ...util.funcutils import is_none

"""
Protocolar handler of the secure connection with the server
"""


class ProtocolHandler(asyncio.Protocol):
    """
    The secure protocol handler used to communicate with the server.
    The first state is S0. Some state objects are responsible of choosing
    the next state.

    Attribute(s):
    - core: the ClientCore instance
    - loop: the asynchronous input/output loop
    - states: sequence of state objects
    - state: the actual state (set in connection_made and changed by states)
    - lock: lock object for serializing thread execution
    - config: the client configuration as a list of curve and cipher names
    - transport: the SSL socket
    - password: the client password (set by the UI)
    - login: the client login (set by the UI)
    - ephecc: the ephemeral server public key (set by S0 state)
    - ms: the client master secret (set by S1S state)
    - session: the client session number (set by S1CR state)
    - keyH: the client key handler (set by S31A state)

    Method(s):
    - connection_made: method called when the connection with the server is made
    - data_received: method called each time a new data is received
    - connection_lost: method called when the connection is lost or closed
    - exception_handler: method called when an exception is raised by a state
    - notify: notify ClientCore a property has changed
    """

    def __init__(self, core):
        """Object initialization"""
        self.core = core
        self.loop = core.loop
        self.password = self.login = 'None'
        # The protocol states
        self.states = {'0': StateS0(),
                       '1S': StateS1S(), '1CR': StateS1CR(), '1CA': StateS1CA(),
                       '21R': StateS21R(), '21A': StateS21A(),
                       '22R': StateS22R(), '22A': StateS22A(),
                       '31R': StateS31R(), '31A': StateS31A(),
                       '32R': StateS32R(), '32A': StateS32A(),
                       '33R': StateS33R(), '33A': StateS33A(),
                       '34R': StateS34R(), '34A': StateS34A(),
                       '35R': StateS35R(), '35A': StateS35A(),
                       '36R': StateS36R(), '36A': StateS36A(),
                       '37R': StateS37R(), '37A': StateS37A()}
        # The client configuration
        self.config = is_none(Configuration.curve1) + ";" + \
            is_none(Configuration.cipher1) + ";" + \
            is_none(Configuration.curve2) + ";" + \
            is_none(Configuration.cipher2) + ";" + \
            is_none(Configuration.curve3) + ";" + is_none(Configuration.cipher3)
        # Lock object for serializing thread execution
        self.lock = threading.Lock()

    def connection_made(self, transport):
        """See mother class"""
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        self.state = self.states['0']  # State 0 at the beginning

    def data_received(self, data):
        """See mother class"""
        # Wait for actual execution before scheduling a new execution
        with self.lock:
            self.loop.run_in_executor(None, self.state.do, self,
                                      data)  # Future execution

    def connection_lost(self, exc):
        """See mother class"""
        if exc:
            self.loop.run_in_executor(None, self.notify,
                                      'connection.state.error',
                                      str(exc).capitalize())
        else:
            self.loop.run_in_executor(None, self.notify,
                                      'connection.state.error',
                                      'Connection closed')
        asyncio.run_coroutine_threadsafe(self.core.close(), self.loop)

    def exception_handler(self, exc):
        """Exception handler for actions executed by the executor"""
        self.loop.run_in_executor(None, self.notify, 'connection.state.error',
                                  str(exc).capitalize()[:50] + '...')
        asyncio.run_coroutine_threadsafe(self.core.close(), self.loop)

    def notify(self, key, value):
        """Notify ClientCore a property has changed"""
        self.core.update(key, value)

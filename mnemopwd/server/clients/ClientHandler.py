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

import asyncio
import logging
from server.clients.protocol import *

"""
The client connection handler
"""

class ClientHandler(asyncio.Protocol):
    """The client connection handler"""
    
    def __init__(self, loop, path):
        """Initialize the handler"""
        self.db_path = path # The path to the database
        self.loop = loop # The i/o asynchronous loop
        # The protocol states
        self.states = {'0':StateS0(), '11':StateS11(), '12':StateS12(), '2':StateS2()}
        
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

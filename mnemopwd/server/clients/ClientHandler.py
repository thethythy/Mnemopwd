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

"""
Handler of a client connection
"""

class ClientHandler(asyncio.Protocol):
    """A client connection handler"""
    
    def connection_made(self, transport):
        """Connection starting"""
        self.peername = transport.get_extra_info('peername')
        cipher = transport.get_extra_info('cipher')
        logging.info('Connection from {} with {}'.format(self.peername,cipher))
        self.transport = transport
        
    def connection_lost(self, exc):
        """Connection finishing"""
        if exc is None:
            logging.info('Disconnection from {}'.format(self.peername))
        else:
            logging.warning('Lost connection from {}'.format(self.peername))
        self.transport.close()

    def data_received(self, data):
        """Data received"""
        message = data.decode()
        print('Data received: {!r}'.format(message))

        print('Send: {!r}'.format(message))
        self.transport.write(data)

        #print('Close the client socket')
        #self.transport.close()
        
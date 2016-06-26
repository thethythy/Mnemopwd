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

import logging
import asyncio
import socket
import ssl
import time
import concurrent.futures
import functools
from client.util.Configuration import Configuration
from client.util.funcutils import Subject
from client.corelayer.protocol.ProtocolHandler import ProtocolHandler
from common.SecretInfoBlock import SecretInfoBlock

"""
Client part of Mnemopwd application.
"""

class ClientCore(Subject):
    """
    Client module of the application

    Attribut(s):
    - loop: an i/o asynchronous loop (see the official asyncio module)
    - queue: a FIFO task queue for handling commands coming from the UI layer
    - transport: a SSL/TLS asynchronous socket (see the official ssl module)
    - protocol: a communication handler (see the official asyncio module)
    - table: block table (a dictionary)

    Method(s):
    - start: start the domain layer
    - stop: close the domain loop
    - command: execute a command coming from UI layer
    - _open: open a new connection to the server
    - _close: close the connection
    - _setCredentials: set login/password then start S1 state
    """

    # Intern methods

    def __init__(self):
        """Initialization"""
        Subject.__init__(self)

        # Create an i/o asynchronous loop
        self.loop = asyncio.get_event_loop()
        if Configuration.loglevel is not None:
            self.loop.set_debug(Configuration.loglevel == 'DEBUG')
            logging.basicConfig(filename="client.log", \
                                level=Configuration.loglevel, \
                                format='%(asctime)s %(process)d %(levelname)s %(message)s', \
                                datefmt='%m/%d/%Y %I:%M:%S')

        # Create a task queue
        self.queue = asyncio.Queue(maxsize=Configuration.queuesize, loop=self.loop)

        # Create and set an executor
        executor = concurrent.futures.ThreadPoolExecutor(Configuration.poolsize)
        self.loop.set_default_executor(executor)

        # Create a SSL context
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.options |= ssl.OP_NO_SSLv2 # SSL v2 not allowed
        self.context.options |= ssl.OP_NO_SSLv3 # SSL v3 not allowed
        self.context.verify_mode = ssl.CERT_OPTIONAL # Server certificat is optional
        self.context.check_hostname = False # Don't check hostname because of shared certificat
        if Configuration.certfile != 'None' :
            self.context.load_verify_locations(cafile=Configuration.certfile) # Load certificat
        else:
            self.context.set_ciphers("AECDH-AES256-SHA") # Cipher suite to use

        if Configuration.action == 'status':
            self._open() # Try to open a connection to server
            print("the server seems running at " + str(self.transport.get_extra_info('peername')))

    def _open(self):
        """Open a new connection to the server"""
        # Block table
        self.table = {}

        # Create an asynchronous SSL socket
        coro = self.loop.create_connection(lambda: ProtocolHandler(self), \
                                           Configuration.server, Configuration.port, \
                                           family=socket.AF_INET, ssl=self.context)
        # Try to open SSL socket
        try:
            if not self.loop.is_running():
                self.transport, self.protocol = self.loop.run_until_complete(coro)
            else:
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                self.transport, self.protocol = future.result(Configuration.timeout)

        except asyncio.TimeoutError:
            future.cancel()
            self.update('connection.state', 'Enable to connect to server. Retry or verify your configuration')
            raise
        except ConnectionRefusedError as e:
            if not self.loop.is_running():
                print(e)
                print("Enable to connect to server. Retry or verify your configuration")
            else:
                self.update('connection.state', 'Enable to connect to server. Retry or verify your configuration')
            raise
        except ssl.SSLError as e:
            if not self.loop.is_running():
                print(e)
                print("There is a problem with the certificat.")
            else:
                self.update('connection.state', 'There is a problem with the certificat.')
            raise
        except Exception as e:
            if not self.loop.is_running():
                print(e)
            else:
                self.update('connection.state', 'An unexpected exception occurred')
            raise

    def _setCredentials(self, login, password):
        """Store login and password then start state S1"""
        self.protocol.login = login.encode()
        self.protocol.password = password.encode()
        # Wait for being in state number one
        while self.protocol.state != self.protocol.states['1S']: time.sleep(0.01)
        # Schedule execution of actual protocol state
        self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, None)

    @asyncio.coroutine
    def _commandHandler(self):
        """Task execution loop"""
        while True:
            task = yield from self.queue.get()
            yield from asyncio.wait_for(task, None)
            self.update('connection.state', 'Task Done')

    @asyncio.coroutine
    def _close(self):
        """Close the connection and empty queue"""
        self.taskInProgress = False
        yield from self.transport.close()
        self.queue = asyncio.Queue(maxsize=Configuration.queuesize, loop=self.loop)

    @asyncio.coroutine
    def _task_close(self):
        """Close the connection with the server"""
        self._close()
        self.update('connection.state.logout', 'Connection closed')

    @asyncio.coroutine
    def _task_addDataOrUpdateData(self, idBlock, values):
        """Add a new block or update an existing block"""
        if idBlock == 0:
            self.protocol.state = self.protocol.states['35R'] # Add a new block
        else:
            self.protocol.state = self.protocol.states['37R'] # Update an existing block

        # Create a block
        self.lastblock = SecretInfoBlock(self.protocol.keyH)
        self.lastblock.nbInfo = len(values)
        i = 1
        for value in values:
            self.lastblock['info' + str(i)] = value
            i += 1

        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, self.lastblock)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    def _deleteData(self, idBlock):
        """Delete an existing block"""
        self.protocol.state = self.protocol.states['36R']
        self.lastblock = idBlock
        # Schedule execution of actual protocol state
        self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, idBlock)

    @asyncio.coroutine
    def _task_searchData(self, pattern):
        """Search blocks matching a pattern"""
        self.protocol.state = self.protocol.states['34R'] # Search
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, pattern)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    def _exportData(self):
        """Get all blocks"""
        pass
        #self.protocol.state = self.protocol.states['32R']
        # Schedule execution of actual protocol state
        #self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, pattern)

    # Extern methods

    def start(self):
        """Start the main loop"""
        self.cmdH = self.loop.create_task(self._commandHandler()) # Command loop
        self.loop.run_forever() # Run until the end of the main loop
        self.loop.close()       # Close the main loop

    def stop(self):
        """Close the connection to the server then stop the main loop"""
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.cmdH.cancel) # Ask for cancelling the command loop
            while not self.cmdH.cancelled(): time.sleep(0.01) # Waiting cancellation
            self.loop.call_soon_threadsafe(self.loop.stop) # Ask for stopping the main loop
        else:
            self.transport.close()
            self.loop.close()

    def command(self, property, value):
        """Create and enqueue a task from a command coming from UI layer"""
        task = None
        if property == "connection.open.credentials":
            # Direct execution because queue is empty at this moment
            self._open()
            self._setCredentials(*value)
        if property == "connection.close":
            task = self._task_close()
        if property == "application.editblock":
            task = self._task_addDataOrUpdateData(*value)
        if property == "application.deleteblock":
            self._deleteData(*value)
        if property == "application.searchblock":
            task = self._task_searchData(value)
        if property == "application.exportblock":
            self._exportData()

        if task is not None:
            asyncio.run_coroutine_threadsafe(self.queue.put(task), self.loop)

    def assignLastSIB(self, index):
        """Callback method for assignation of last block used"""
        if self.lastblock: self.table[index] = self.lastblock
        self.lastblock = None

    def removeLastSIB(self):
        """Callback method for removing last block used"""
        if self.lastblock: del self.table[self.lastblock]
        self.latsblock = None

    def assignSIB(self, index_sib, sib):
        """Callback method for assignation of a block"""
        self.table[index_sib] = sib


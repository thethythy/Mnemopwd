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
from client.util.Configuration import Configuration
from client.util.funcutils import Subject
from client.corelayer.protocol.ProtocolHandler import ProtocolHandler
from common.SecretInfoBlock import SecretInfoBlock

"""
Client part of MnemoPwd application.
"""


class ClientCore(Subject):
    """
    Client module of the application

    Attribute(s):
    - loop: an i/o asynchronous loop (see the official asyncio module)
    - queue: a FIFO task queue for handling commands coming from the UI layer
    - transport: a SSL/TLS asynchronous socket (see the official ssl module)
    - protocol: a communication handler (see the official asyncio module)
    - table: table of blocks (a dictionary)

    Method(s):
    - start: start the domain layer
    - stop: close the domain loop
    - command: execute a command coming from the UI layer
    - close: close the connection
    """

    # Internal methods

    def __init__(self):
        """Initialization"""
        Subject.__init__(self)

        # Create an i/o asynchronous loop
        self.loop = asyncio.get_event_loop()
        if Configuration.loglevel is not None:
            self.loop.set_debug(Configuration.loglevel == 'DEBUG')
            logging.basicConfig(filename="client.log",
                                level=Configuration.loglevel,
                                format='%(asctime)s %(process)d %(levelname)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S')

        # Create a task queue
        self.queue = asyncio.Queue(maxsize=Configuration.queuesize, loop=self.loop)
        self.cmdH = None  # The command handler co-routine
        self.taskInProgress = False  # Flag to indicate a task is in progress
        self.lastblock = None  # The last block or the last index used

        # Create and set an executor
        executor = concurrent.futures.ThreadPoolExecutor(Configuration.poolsize)
        self.loop.set_default_executor(executor)

        # Create a SSL context
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.options |= ssl.OP_NO_SSLv2  # SSL v2 not allowed
        self.context.options |= ssl.OP_NO_SSLv3  # SSL v3 not allowed
        self.context.verify_mode = ssl.CERT_OPTIONAL  # Server certificat is optional
        self.context.check_hostname = False  # Don't check hostname because of shared certificat
        if Configuration.certfile != 'None':
            self.context.load_verify_locations(cafile=Configuration.certfile)  # Load certificat
        else:
            self.context.set_ciphers("AECDH-AES256-SHA")  # Cipher suite to use

        if Configuration.action == 'status':
            self._open()  # Try to open a connection to server
            print("the server seems running at " + str(self.transport.get_extra_info('peername')))

    def _open(self):
        """Open a new connection to the server"""
        # Block table
        self.table = {}

        # Create an asynchronous SSL socket
        coro = self.loop.create_connection(lambda: ProtocolHandler(self),
                                           Configuration.server, Configuration.port,
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
                exit(1)
            else:
                self.update('connection.state', 'Enable to connect to server. Retry or verify your configuration')
                raise
        except ssl.SSLError as e:
            if not self.loop.is_running():
                print(e)
                print("There is a problem with the certificat.")
                exit(1)
            else:
                self.update('connection.state', 'There is a problem with the certificat.')
                raise
        except Exception as e:
            if not self.loop.is_running():
                print(e)
                exit(1)
            else:
                self.update('connection.state', 'An unexpected exception occurred')
                raise

    @asyncio.coroutine
    def _command_handler(self):
        """Tasks' execution loop"""
        while True:
            task = yield from self.queue.get()
            yield from asyncio.wait_for(task, None)

    @asyncio.coroutine
    def _task_set_credentials(self, login, password):
        """Store login and password then start state S1"""
        self.protocol.login = login.encode()
        self.protocol.password = password.encode()
        # Wait for being in state number one
        while self.protocol.state != self.protocol.states['1S']:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Execute protocol state
        self.taskInProgress = True
        self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, None)
        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    @asyncio.coroutine
    def _task_new_credentials(self, login, password):
        """Start state S1"""
        Configuration.first_execution = True
        yield from self._task_set_credentials(login, password)
        Configuration.first_execution = False

    @asyncio.coroutine
    def _task_close(self):
        """Close the connection with the server"""
        self.taskInProgress = False
        self.queue = asyncio.Queue(maxsize=Configuration.queuesize, loop=self.loop)
        self.transport.close()
        yield from self.loop.run_in_executor(None, self.update, 'connection.state.logout', 'Connection closed')

    @asyncio.coroutine
    def _task_deletion(self):
        """User account deletion request"""
        self.protocol.state = self.protocol.states['33R']  # Deletion
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, None)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    @asyncio.coroutine
    def _task_add_data_or_update_data(self, idblock, values):
        """Add a new block or update an existing block"""
        if idblock is None:
            self.protocol.state = self.protocol.states['35R']  # Add a new block
        else:
            self.protocol.state = self.protocol.states['37R']  # Update an existing block

        # Create a block
        self.lastblock = SecretInfoBlock(self.protocol.keyH)
        self.lastblock.nbInfo = len(values)
        i = 1
        for value in values:
            self.lastblock['info' + str(i)] = value.encode()
            i += 1

        # Execute protocol state
        self.taskInProgress = True
        if idblock is None:
            yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, self.lastblock)
        else:
            yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, (idblock, self.lastblock))

        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

        # Assign updated block
        if idblock is not None:
            self.assign_last_block(idblock)

    @asyncio.coroutine
    def _task_delete_data(self, idblock):
        """Delete an existing block"""
        self.protocol.state = self.protocol.states['36R']  # Delete
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, idblock)
        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Remove block
        del self.table[idblock]

    @asyncio.coroutine
    def _task_search_data(self, pattern):
        """Search blocks matching a pattern"""
        self.protocol.state = self.protocol.states['34R']  # Search
        self.searchTable = list()  # Reset search table
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, pattern)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Notify the result to the UI layer
        if len(self.searchTable) > 0:
            yield from self.loop.run_in_executor(None, self.update, 'application.searchblock.result', self.searchTable)

    @asyncio.coroutine
    def _task_export_data(self):
        """Get all blocks"""
        self.protocol.state = self.protocol.states['32R']  # Export
        self.searchTable = list()  # Reset search table
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(None, self.protocol.state.do, self.protocol, None)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Notify the result to UI layer
        if len(self.searchTable) > 0:
            yield from self.loop.run_in_executor(None, self.update, 'application.searchblock.result', self.searchTable)

    @asyncio.coroutine
    def _task_get_block_values(self, index):
        """Return values of a block"""
        values = list()
        sib = self.table[index]
        for j in range(1, sib.nbInfo + 1):  # For all info in sib
            values.append(sib['info' + str(j)].decode())
        # Notify the result to UI layer
        yield from self.loop.run_in_executor(None, self.update, 'application.searchblock.oneresult', (index, values))

    # External methods

    @asyncio.coroutine
    def close(self):
        """Close the connection and empty the queue"""
        self.taskInProgress = False
        self.queue = asyncio.Queue(maxsize=Configuration.queuesize, loop=self.loop)
        self.transport.close()

    def start(self):
        """Start the main loop"""
        self.cmdH = self.loop.create_task(self._command_handler())  # Command loop
        self.loop.run_forever()  # Run until the end of the main loop
        self.loop.close()        # Close the main loop

    def stop(self):
        """Close the connection to the server then stop the main loop"""
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.cmdH.cancel)  # Ask for cancelling the command loop
            while not self.cmdH.cancelled():
                time.sleep(0.01)  # Waiting cancellation
            self.loop.call_soon_threadsafe(self.loop.stop)  # Ask for stopping the main loop
        else:
            self.transport.close()
            self.loop.close()

    def command(self, key, value):
        """Create and enqueue a task from a command coming from UI layer"""
        task = None

        if key == "connection.open.credentials":
            try:
                self._open()  # Direct execution because queue is empty at this moment
                task = self._task_set_credentials(*value)
            except:
                pass
        if key == "connection.open.newcredentials":
            try:
                self._open()  # Direct execution because queue is empty at this moment
                task = self._task_new_credentials(*value)
            except:
                pass
        if key == "connection.close":
            task = self._task_close()
        if key == "connection.close.deletion":
            task = self._task_deletion()
        if key == "application.editblock":
            task = self._task_add_data_or_update_data(*value)
        if key == "application.deleteblock":
            task = self._task_delete_data(value)
        if key == "application.searchblock":
            task = self._task_search_data(value)
        if key == "application.exportblock":
            task = self._task_export_data()
        if key == "application.searchblock.blockvalues":
            task = self._task_get_block_values(value)

        if task is not None:
            asyncio.run_coroutine_threadsafe(self.queue.put(task), self.loop)

    def assign_last_block(self, index):
        """Callback method for assignation of last block used"""
        if self.lastblock:
            self.table[index] = self.lastblock
        self.lastblock = None

    def assign_result_search_block(self, index_sib, sib):
        """Callback method for assignation of a search result"""
        self.table[index_sib] = sib
        self.searchTable.append(index_sib)

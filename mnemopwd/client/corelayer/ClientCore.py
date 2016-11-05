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
import os

from ..util.Configuration import Configuration
from ..util.funcutils import Subject
from .protocol.ProtocolHandler import ProtocolHandler

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
                                format='%(asctime)s %(levelname)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S')
        else:
            logging.basicConfig(filename=os.devnull)

        # Create a task queue
        self.queue = asyncio.Queue(
            maxsize=Configuration.queuesize, loop=self.loop)
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
        # Server certificate is optional
        self.context.verify_mode = ssl.CERT_OPTIONAL
        # Don't check hostname because of shared certificate
        self.context.check_hostname = False
        if Configuration.certfile != 'None':
            # Load certificate
            self.context.load_verify_locations(cafile=Configuration.certfile)
        else:
            self.context.set_ciphers("AECDH-AES256-SHA")  # Cipher suite to use

        # Transport handler
        self.transport = None

        if Configuration.action == 'status':
            self._open()  # Try to open a connection to server
            print("the server seems running at " +
                  str(self.transport.get_extra_info('peername')))

    def _open(self):
        """Open a new connection to the server"""
        # Block table
        self.table = {}

        # Create an asynchronous SSL socket
        coro = self.loop.create_connection(
            lambda: ProtocolHandler(self), Configuration.server,
            Configuration.port, family=socket.AF_INET, ssl=self.context)
        # Try to open SSL socket
        try:
            if not self.loop.is_running():
                self.transport, self.protocol = self.loop.run_until_complete(coro)
            else:
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                self.transport, self.protocol = future.result(Configuration.timeout)

        except asyncio.TimeoutError:
            future.cancel()
            self.update(
                'connection.state',
                'Enable to connect to server. Retry or verify your configuration')
            raise
        except ConnectionRefusedError as e:
            if not self.loop.is_running():
                print(e)
                print("Enable to connect to server. Retry or verify your configuration")
                exit(1)
            else:
                self.update(
                    'connection.state',
                    'Enable to connect to server. Retry or verify your configuration')
                raise
        except ssl.SSLError as e:
            if not self.loop.is_running():
                print(e)
                print("There is a problem with the certificate.")
                exit(1)
            else:
                self.update('connection.state',
                            'There is a problem with the certificate.')
                raise
        except Exception as e:
            if not self.loop.is_running():
                print(e)
                exit(1)
            else:
                self.update('connection.state',
                            'An unexpected exception occurred')
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
        yield from self.loop.run_in_executor(
            None, self.protocol.data_received, None)
        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    @asyncio.coroutine
    def _task_close(self):
        """Close the connection with the server"""
        yield from self.loop.run_in_executor(
            None, self.update, 'connection.state.logout', 'Connection closed')
        self.queue = asyncio.Queue(
            maxsize=Configuration.queuesize, loop=self.loop)
        self.taskInProgress = False
        self.transport.close()
        self.transport = None

    @asyncio.coroutine
    def _task_deletion(self):
        """User account deletion request"""
        self.protocol.state = self.protocol.states['33R']  # Deletion
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(
            None, self.protocol.data_received, None)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

    @asyncio.coroutine
    def _task_add_data_or_update_data(self, idblock, sib):
        """Add a new block or update an existing block"""
        if idblock is None:
            # Add a new block
            self.protocol.state = self.protocol.states['35R']
        else:
            # Update an existing block
            self.protocol.state = self.protocol.states['37R']

        # Remember the block
        self.lastblock = sib

        # Execute protocol state
        self.taskInProgress = True
        if idblock is None:
            yield from self.loop.run_in_executor(
                None, self.protocol.data_received, self.lastblock)
        else:
            yield from self.loop.run_in_executor(
                None, self.protocol.data_received, (idblock, self.lastblock))

        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)

        # Assign updated block
        if idblock is not None:
            yield from self.assign_last_block(idblock, 'update')

    @asyncio.coroutine
    def _task_delete_data(self, idblock):
        """Delete an existing block"""
        self.protocol.state = self.protocol.states['36R']  # Delete
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(
            None, self.protocol.data_received, idblock)
        # Waiting for the end of the task
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Remove block
        del self.table[idblock]
        # Notify the result to UI layer
        yield from self.loop.run_in_executor(
            None, self.update, 'application.searchblock.removeresult', idblock)

    @asyncio.coroutine
    def _task_search_data(self, pattern):
        """Search blocks matching a pattern"""
        self.protocol.state = self.protocol.states['34R']  # Search
        self.searchTable = list()  # Reset search table
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(
            None, self.protocol.data_received, pattern)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Notify the result to the UI layer
        if len(self.searchTable) > 0:
            yield from self.loop.run_in_executor(
                None, self.update, 'application.searchblock.result',
                self.searchTable)

    @asyncio.coroutine
    def _task_export_data(self):
        """Get all blocks"""
        self.protocol.state = self.protocol.states['32R']  # Export
        self.searchTable = list()  # Reset search table
        # Execute protocol state
        self.taskInProgress = True
        yield from self.loop.run_in_executor(
            None, self.protocol.data_received, None)
        while self.taskInProgress:
            yield from asyncio.sleep(0.01, loop=self.loop)
        # Notify the result to UI layer
        if len(self.searchTable) > 0:
            yield from self.loop.run_in_executor(
                None, self.update, 'application.searchblock.result',
                self.searchTable)

    @asyncio.coroutine
    def _task_get_block_values(self, idblock):
        """Return values of a block"""
        sib = self.table[idblock]
        # Notify the result to UI layer
        yield from self.loop.run_in_executor(
            None, self.update, 'application.searchblock.oneresult',
            (idblock, sib))

    # External methods

    @asyncio.coroutine
    def close(self):
        """Close the connection and empty the queue"""
        if self.transport is not None:
            self.queue = asyncio.Queue(
                maxsize=Configuration.queuesize, loop=self.loop)
            self.taskInProgress = False
            self.transport.close()
            self.transport = None

    def start(self):
        """Start the main loop"""
        # Command loop
        self.cmdH = self.loop.create_task(self._command_handler())
        # Run until the end of the main loop
        self.loop.run_forever()
        # Close the main loop
        self.loop.close()

    def stop(self):
        """Close the connection to the server then stop the main loop"""
        if self.loop.is_running():
            # Waiting for the queue becomes empty
            while not self.queue.empty():
                time.sleep(0.01)
            # Ask for cancelling the command loop
            self.loop.call_soon_threadsafe(self.cmdH.cancel)
            # Waiting for cancellation
            while not self.cmdH.cancelled():
                time.sleep(0.01)
            # Ask for stopping the main loop
            self.loop.call_soon_threadsafe(self.loop.stop)
        else:
            self.transport.close()
            self.loop.close()

    def command(self, key, value):
        """Create and enqueue a task from a command coming from UI layer"""
        task = None

        if key == "connection.open.credentials":
            try:
                # Direct execution because queue is empty at this moment
                self._open()
                task = self._task_set_credentials(*value)
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

    @asyncio.coroutine
    def assign_last_block(self, idblock, task):
        """Callback method for assignation of last block used"""
        # Notify the result to UI layer
        if task == 'add':
            yield from self.loop.run_in_executor(
                None, self.update, 'application.searchblock.tryoneresult',
                (idblock, self.lastblock))
        elif task == 'update':
            yield from self.loop.run_in_executor(
                None, self.update, 'application.searchblock.updateresult',
                (idblock, self.lastblock))
        # Update table
        self.table[idblock] = self.lastblock
        self.lastblock = None

    def assign_result_search_block(self, idblock, sib):
        """Callback method for assignation of a search result"""
        self.table[idblock] = sib
        self.searchTable.append(idblock)

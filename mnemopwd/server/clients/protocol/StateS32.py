# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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

"""
State S32 : exportation operation
"""
import logging
import pickle
import asyncio

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS32(StateSCC):
    """State S32 : export all secret information blocks"""

    def do(self, client, data):
        """Action of the state S32: return a sequence of all secret
        information blocks"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S32.4'):

                # Test for S32 command
                is_cd_S32 = data[170:181] == b"EXPORTATION"
                if not is_cd_S32:
                    raise Exception('S32 protocol error')

                # Get all sibs
                tabsibs = client.dbH.get_data(client.keyH)

                # Send number of blocks
                msg = b'OK;' + str(len(tabsibs)).encode()
                client.loop.call_soon_threadsafe(client.transport.write, msg)

                # Send sib one by one
                for i, sib in tabsibs:
                    si = str(i).encode()
                    psib = pickle.dumps(sib)
                    lpsib = str(len(psib)).encode()
                    # Send message
                    msg = b';SIB;' + si + b';' + lpsib + b';' + psib
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    # Wait for sending the message
                    coro = asyncio.sleep(0.005, loop=client.loop)
                    future = asyncio.run_coroutine_threadsafe(coro, client.loop)
                    future.result(1)

                client.state = client.states['3']  # New client state

                logging.info('Exporting [{} blocks] to {}'
                             .format(len(tabsibs), client.peername))

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

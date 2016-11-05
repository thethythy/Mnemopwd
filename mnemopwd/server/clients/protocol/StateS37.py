# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016, Thierry Lemeunier <thierry at lemeunier dot net>
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
State S37 : update data operation
"""

import pickle
import logging

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS37(StateSCC):
    """State S37 : update a secret information block"""

    def do(self, client, data):
        """Action of the state S37: update a secret information block"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S37.5'):

                # Test for S37 command
                is_cd_S37 = data[170:180] == b"UPDATEDATA"
                if not is_cd_S37:
                    raise Exception('S37 protocol error')

                protocol_data = data[181:].split(b';', maxsplit=1)

                index = protocol_data[0].decode() # sib index
                bsib = protocol_data[1] # sib in pickle encoding

                try:
                    sib = pickle.loads(bsib) # sib object
                    sib.control_integrity(client.keyH)  # Configure + integrity

                except AssertionError:
                    # Send an error message
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('S37 data rejected')

                else:
                    # Update a secret information block
                    result = client.dbH.update_data(index, sib)

                    if result:
                        # Send 'OK' message
                        client.loop.call_soon_threadsafe(
                            client.transport.write, b'OK')
                        client.state = client.states['3']  # New client state
                    else:
                        msg = b'ERROR;application protocol error'
                        client.loop.call_soon_threadsafe(
                            client.transport.write, msg)
                        raise Exception('S37 index rejected')

                    logging.info('Update block from {}'.format(client.peername))

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

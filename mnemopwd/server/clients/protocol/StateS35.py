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
State S35 : add data operation
"""

import pickle
import logging

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS35(StateSCC):
    """State S35 : add a secret information block"""

    def do(self, client, data):
        """Action of the state S35: add a secret information block"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S35.6'):

                # Test for S35 command
                is_cd_S35 = data[170:177] == b"ADDDATA"
                if not is_cd_S35:
                    raise Exception('S35 protocol error')

                bsib = data[178:]  # A secret information block in pickle format

                try:
                    sib = pickle.loads(bsib)  # A secret information block
                    sib.control_integrity(client.keyH)  # Configure + integrity

                except AssertionError:
                    # Send an error message
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('S35 data rejected')

                else:
                    # Add a secret information block
                    index = client.dbH.add_data(sib)
                    # Send index value
                    msg = b'OK;' + (str(index)).encode()
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    client.state = client.states['3']  # New client state

                    logging.info('New block from {}'.format(client.peername))

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

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
State S31 : configuration operation
"""

import logging

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS31(StateSCC):
    """State S31 : configuration of the cryptographic handler"""

    def do(self, client, data):
        """Action of the state S31: obtain (and eventually change)
        cryptographic configuration"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S31.6'):

                # Test for S31 command
                is_cd_S31 = data[170:183] == b"CONFIGURATION"
                if not is_cd_S31:
                    raise Exception('S31 protocol error')

                econfig = data[184:]    # Encrypted configuration string
                config = client.ephecc.decrypt(econfig)  # Decrypting

                # Try to configure client cryptographic handler
                result = client.configure_crypto(config.decode())

                if result is False:
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('S31 wrong configuration {}'
                                    .format(config.decode()))

                else:

                    if result == 1:
                        # Send result value
                        msg = b'OK;' + b'1'
                        client.loop.call_soon_threadsafe(
                            client.transport.write, msg)

                    if result == 2:
                        if client.update_crypto():  # Re-do encryption
                            # Send result value
                            msg = b'OK;' + b'2'
                            client.loop.call_soon_threadsafe(
                                client.transport.write, msg)
                        else:
                            msg = b'ERROR;application protocol error'
                            client.loop.call_soon_threadsafe(
                                client.transport.write, msg)
                            raise Exception('S31 operation aborted')

                    client.state = client.states['3']  # New client state

                    logging.info('Configuration done from {}'
                                 .format(client.peername))

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

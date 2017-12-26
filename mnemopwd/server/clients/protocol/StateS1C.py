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
State S1C : Challenge
"""

import logging

from ....pyelliptic import hmac_sha256
from ...util.funcutils import singleton


@singleton
class StateS1C:
    """State S1C : control challenge answer"""

    def do(self, client, data):
        """Action of the state S1C: control challenge answer"""

        try:
            # Test for S1C command
            is_cd_S1C = data[:10] == b"CHALLENGEA"
            if not is_cd_S1C:
                raise Exception('S1C protocol error')

            echallenge = data[11:]  # Encrypted challenge
            challenge = client.ephecc.decrypt(echallenge)  # Decrypting

            # Compute challenge
            challenge_bis = hmac_sha256(client.ms, client.session + b'S1.13')

            if challenge == challenge_bis:
                # Send challenge accepted
                client.loop.call_soon_threadsafe(client.transport.write, b'OK')
            else:
                # Send challenge rejected
                msg = b'ERROR;application protocol error'
                client.loop.call_soon_threadsafe(client.transport.write, msg)
                raise Exception("challenge rejected")

            logging.info('Session opened with {}'.format(client.peername))

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

        else:
            client.state = client.states['2']  # Next state

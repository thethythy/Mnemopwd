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


"""
State SO : KeySharing
"""

from ...util.funcutils import singleton
from ....pyelliptic import ECC


@singleton
class StateS0:
    """State S0 : KeySharing"""

    def do(self, handler, data):
        """Action of the state S0: get the ephemeral server public key"""
        with handler.lock:
            try:
                # Test for S1C command
                is_cd_S0C = data[:10] == b"KEYSHARING"
                if not is_cd_S0C:
                    raise Exception('S0 protocol error')

                # Test for ephemeral server public key
                protocol_data = data[11:]
                ephecc = ECC(pubkey=protocol_data)
                try:
                    assert protocol_data == ephecc.get_pubkey()
                except AssertionError:
                    raise Exception('bad ephemeral server public key')

                # Notify the handler a property has changed
                handler.loop.run_in_executor(None, handler.notify,
                                             "connection.state",
                                             "Waiting for login/password")

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

            else:
                handler.ephecc = ephecc  # Store the ephemeral public key
                handler.state = handler.states['1S']  # Next state

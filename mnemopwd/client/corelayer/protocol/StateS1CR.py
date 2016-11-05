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
State S1 : Session
"""

from ...util.funcutils import singleton
from ....pyelliptic import OpenSSL
from ....pyelliptic import Cipher
from ....pyelliptic import hmac_sha256


@singleton
class StateS1CR:
    """State S1CR : Session"""

    def do(self, handler, data):
        """Action of the state S1CR: answer the challenge request"""
        with handler.lock:
            try:
                # Test for S1CR command
                is_cd_S1CR = data[:10] == b"CHALLENGER"
                if not is_cd_S1CR:
                    raise Exception('S1CR protocol error')

                # Get esession number
                blocksize = OpenSSL.get_cipher('aes-256-cbc').get_blocksize()
                iv = data[11:11 + blocksize]
                esession = data[12 + blocksize:]

                # Decrypt session number
                ctx = Cipher(handler.ms, iv, 0, 'aes-256-cbc')
                session = ctx.ciphering(esession)

                # Compute challenge answer
                challenge = hmac_sha256(handler.ms, session + b'S1.12')

                # Encrypt challenge answer
                echallenge = handler.ephecc.encrypt(
                    challenge, pubkey=handler.ephecc.get_pubkey())

                # Send challenge answer
                msg = b'CHALLENGEA;' + echallenge
                handler.loop.call_soon_threadsafe(handler.transport.write, msg)

                # Notify the handler a property has changed
                handler.loop.run_in_executor(None, handler.notify,
                                             "connection.state",
                                             "Sending challenge answer")

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

            else:
                handler.session = session  # Store the session number
                handler.state = handler.states['1CA']  # Next state

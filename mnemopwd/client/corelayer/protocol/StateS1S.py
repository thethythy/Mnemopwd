# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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

import os

from ...util.funcutils import singleton
from ....pyelliptic import pbkdf2
from ....pyelliptic import Cipher


@singleton
class StateS1S:
    """State S1S : Session"""

    def do(self, handler, data):
        """Action of the state S1S: send the master secret"""
        with handler.lock:
            try:
                # Compute the master secret
                salt, ms = pbkdf2(handler.password, salt=handler.login, hfunc='SHA1')
                ems = handler.ephecc.encrypt(ms, pubkey=handler.ephecc.get_pubkey())

                # Compute the session number
                nonce = (os.urandom(32))  # Random nonce (32 bytes)
                iv = Cipher.gen_IV('aes-256-cbc')
                cipher = Cipher(ms, iv, 1, 'aes-256-cbc')
                session = cipher.ciphering(nonce)[:16]  # session (16 bytes)
                esession = handler.ephecc.encrypt(session,
                                                  pubkey=handler.ephecc.get_pubkey())
                len_esession = str(len(esession)).encode()

                # Send session number and master secret encrypted
                msg = b'SESSION;' + len_esession + b';' + esession + b';' + ems
                handler.loop.call_soon_threadsafe(handler.transport.write, msg)

                # Notify the handler a property has changed
                handler.loop.run_in_executor(None, handler.notify,
                                             "connection.state",
                                             "Waiting session number")

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

            else:
                handler.ms = ms  # Store the master secret
                handler.session = session  # Store the session number
                handler.state = handler.states['1CR']  # Next state

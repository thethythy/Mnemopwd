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
State S37 : UpdateData
"""

import pickle

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS37R(StateSCC):
    """State S37 : UpdateData"""

    def do(self, handler, data):
        """Action of the state S37R: send a secret info block update request"""
        with handler.lock:
            try:
                # Challenge creation
                echallenge = self.compute_challenge(handler, b"S37.5")
                if echallenge:
                    # Send UpdateData request
                    idx, sib = data
                    msg = echallenge + b';UPDATEDATA;' + (str(idx)).encode() + \
                        b';' + pickle.dumps(sib)
                    handler.loop.call_soon_threadsafe(handler.transport.write, msg)

                    # Notify the handler a property has changed
                    if handler.core.notify:
                        handler.loop.run_in_executor(
                            None, handler.notify, "application.state",
                            "Update request send to server")

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

            else:
                handler.state = handler.states['37A']  # Next state

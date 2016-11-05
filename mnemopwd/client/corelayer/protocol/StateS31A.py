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
State S31 : Configuration
"""

from ...util.funcutils import singleton
from .StateSCC import StateSCC
from ....common.KeyHandler import KeyHandler


@singleton
class StateS31A(StateSCC):
    """State S31 : Configuration"""

    def do(self, handler, data):
        """Action of the state S31A: treat response of configuration request"""
        with handler.lock:
            try:

                # Test if configuration request is rejected
                is_KO = data[:5] == b"ERROR"
                if is_KO:
                    raise Exception((data[6:]).decode())

                # Test if configuration is accepted
                is_OK = data[:2] == b"OK"
                if is_OK:
                    if data[3:] == b"1":
                        message = "Configuration accepted"
                    elif data[3:] == b"2":
                        message = "New configuration accepted"
                    else:
                        raise Exception("S31 protocol error")

                    # Create the client KeyHandler
                    cypher_suite = handler.config.split(';')
                    handler.keyH = KeyHandler(
                        handler.ms, cur1=cypher_suite[0], cip1=cypher_suite[1],
                        cur2=cypher_suite[2], cip2=cypher_suite[3],
                        cur3=cypher_suite[4], cip3=cypher_suite[5])

                    # Task is ended
                    handler.core.taskInProgress = False

                    # Notify the handler a property has changed
                    handler.loop.run_in_executor(None, handler.notify,
                                                 "application.keyhandler",
                                                 handler.keyH)
                    handler.loop.run_in_executor(None, handler.notify,
                                                 "connection.state", message)

                else:
                    raise Exception("S31 protocol error")

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

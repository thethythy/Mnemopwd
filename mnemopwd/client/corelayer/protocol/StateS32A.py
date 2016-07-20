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
State S32 : Exportation
"""

from client.util.funcutils import singleton
from client.corelayer.protocol.StateSCC import StateSCC
import logging


@singleton
class StateS32A(StateSCC):
    """State S32 : Exportation"""

    def do(self, handler, data):
        """Action of the state S32A: treat response of exportation request"""
        with handler.lock:
            try:
                # Test challenge response
                if self.control_challenge(handler, data):

                    # Test if request is accepted
                    is_OK = data[:2] == b"OK"
                    if is_OK:
                        try:
                            tab_data = data[3:].split(b';', maxsplit=1)
                            nbblock = int(tab_data[0].decode())

                            # Are there SIB to treat ?
                            if nbblock > 0:
                                handler.nbSIB = nbblock  # Number of SIB to treat
                                handler.nbSIBDone = 0  # Number of SIB already treated
                                handler.state = handler.states['32Ab']  # Next state

                                # Check if the first SIB is already received
                                try:
                                    if len(tab_data[1]) > 0:
                                        handler.loop.run_in_executor(None, handler.data_received, b';' + tab_data[1])
                                except IndexError:
                                    pass

                            else:
                                handler.core.taskInProgress = False
                                handler.loop.run_in_executor(None, handler.notify, "application.state",
                                                             "No information found")

                        except:
                            raise Exception("S32A protocol error")

                    else:
                        raise Exception("S32A protocol error")

            except Exception as exc:
                logging.debug(str(data[:50]))
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

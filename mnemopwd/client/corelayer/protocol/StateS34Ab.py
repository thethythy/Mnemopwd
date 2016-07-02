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
State S34 : SearchData
"""

from client.util.funcutils import singleton
from client.corelayer.protocol.StateSCC import StateSCC
import pickle

@singleton
class StateS34Ab(StateSCC):
    """State S34 : SearchData"""

    def do(self, handler, data):
        """Action of the state S34Ab: treat each SIB"""
        with handler.lock:
            try:
                # Test if request is valid
                is_aSIB = data[:5] == b";SIB;"
                if is_aSIB:
                    try:
                        tab_data = data[5:].split(b';', maxsplit=2)
                        index_sib = int(tab_data[0].decode())
                        len_sib = int(tab_data[1].decode())
                        psib = tab_data[2]

                        # Check if two SIB are received in the same packet
                        if len_sib < len(psib):
                            psib = tab_data[2][:len_sib]
                            handler.data_received(b';'+ tab_data[2][len_sib:])

                        if len_sib == len(psib):
                            sib = pickle.loads(psib)
                            sib.control_integrity(handler.keyH)
                            handler.core.assignResultSearchSIB(index_sib, sib)
                            handler.nbSIBDone += 1
                        else:
                            raise Exception("S34Ab protocol error" + str(handler.nbSIBDone))

                        # Notify the UI layer
                        handler.loop.run_in_executor(None, handler.notify,
                            "application.state.loadbar", (handler.nbSIBDone, handler.nbSIB))

                        # Indicate the task is done
                        if handler.nbSIBDone == handler.nbSIB:
                            handler.core.taskInProgress = False

                    except:
                        message = "S34Ab protocol error after " + str(handler.nbSIBDone) + "/" + str(handler.nbSIB) + " blocks"
                        raise Exception(message)

                else:
                    message = "S34Ab protocol error after " + str(handler.nbSIBDone) + "/" + str(handler.nbSIB) + " blocks"
                    raise Exception(message)

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

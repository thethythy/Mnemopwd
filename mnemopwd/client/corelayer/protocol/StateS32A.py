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
State S32 : Exportation
"""

import pickle

from ...util.funcutils import singleton
from .StateSCC import StateSCC


@singleton
class StateS32A(StateSCC):
    """State S32 : Exportation"""

    def __init__(self):
        """Object initialization"""
        self.buffer = None  # Intern buffer

    def do(self, handler, data):
        """Action of the state S32A: treat response of exportation request"""
        with handler.lock:
            try:

                # Test if request is rejected
                is_KO = data[:5] == b"ERROR"
                if is_KO:
                    message = (data[6:]).decode()
                    raise Exception(message)

                # Test if request is accepted
                is_OK = data[:2] == b"OK"
                if is_OK:
                    try:
                        tab_data = data[3:].split(b';', maxsplit=1)
                        nbblock = int(tab_data[0].decode())

                        # Are there SIB to treat ?
                        if nbblock > 0:
                            handler.nbSIB = nbblock  # Number of SIB to treat
                            handler.nbSIBDone = 0  # Number of SIB treated

                            # Check if the first SIB is already received
                            try:
                                if len(tab_data[1]) > 0:
                                    data = b';' + tab_data[1]
                            except IndexError:
                                pass

                        else:
                            handler.core.taskInProgress = False
                            handler.loop.run_in_executor(
                                None, handler.notify, "application.state",
                                "No information found")

                    except:
                        raise Exception("S32A protocol error")

                # Test if a sib has been truncated
                if self.buffer is not None:
                    if self.buffer[5:] == b";SIB;":
                        data = self.buffer + data
                    else:
                        data = data + self.buffer
                    self.buffer = None

                # Test if a sib has been received
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
                            handler.loop.run_in_executor(
                                None, handler.data_received,
                                tab_data[2][len_sib:])

                        # Treat one sib
                        if len_sib == len(psib):
                            sib = pickle.loads(psib)
                            sib.control_integrity(handler.keyH)
                            handler.core.assign_result_search_block(index_sib, sib)
                            handler.nbSIBDone += 1

                            # Notify the UI layer
                            handler.loop.run_in_executor(
                                None, handler.notify, "application.state.loadbar",
                                (handler.nbSIBDone, handler.nbSIB))

                            # Indicate the task is done
                            if handler.nbSIBDone == handler.nbSIB:
                                handler.core.taskInProgress = False
                                self.buffer = None

                        # Not enough data received, wait for new data
                        else:
                            self.buffer = data  # Push data for a next treatment

                    except:
                        message = "S32A protocol error " + \
                                  str(handler.nbSIBDone) + \
                                  "/" + str(handler.nbSIB) + " blocks"
                        raise Exception(message)

                # Save data not treated
                if is_OK is False and is_aSIB is False:
                    self.buffer = data

            except Exception as exc:
                # Schedule a call to the exception handler
                handler.loop.call_soon_threadsafe(handler.exception_handler, exc)

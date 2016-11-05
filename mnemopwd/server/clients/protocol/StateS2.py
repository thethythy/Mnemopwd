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
State S2 : Login or CountCreation
"""

from ...util.funcutils import singleton


@singleton
class StateS2:
    """State S2 : select Login substate (S21) or
    CountCreation substate (S22)"""
        
    def do(self, client, data):
        """Action of the state S2: select substate S21 or S22"""
        
        is_cd_S21 = data[170:175] == b"LOGIN"  # Test for S21 substate
        is_cd_S22 = data[170:178] == b"CREATION"  # Test for S22 substate
        
        if is_cd_S21:
            client.state = client.states['21']  # S21 is the new state
        if is_cd_S22:
            client.state = client.states['22']  # S22 is the new state

        if is_cd_S21 or is_cd_S22:
            # Schedule an execution of the new state
            client.loop.run_in_executor(None, client.state.do, client, data)
        else:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(
                client.exception_handler, Exception('S2 protocol error'))

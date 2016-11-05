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
State S3 : administration or data operations
"""

from ...util.funcutils import singleton


@singleton
class StateS3:
    """State S3 : select substate (S31, S32, S33, S34, S35, S36 or S37) """
        
    def do(self, client, data):
        """Action of the state S3: select a substate"""
        
        is_cd_S31 = data[170:183] == b"CONFIGURATION"   # Test for S31 substate
        is_cd_S32 = data[170:181] == b"EXPORTATION"     # Test for S32 substate
        is_cd_S33 = data[170:178] == b"DELETION"        # Test for S33 substate
        is_cd_S34 = data[170:180] == b"SEARCHDATA"      # Test for S34 substate
        is_cd_S35 = data[170:177] == b"ADDDATA"         # Test for S35 substate
        is_cd_S36 = data[170:180] == b"DELETEDATA"      # Test for S36 substate
        is_cd_S37 = data[170:180] == b"UPDATEDATA"      # Test for S37 substate
        
        if is_cd_S31:
            client.state = client.states['31']  # S31 is the new state
        if is_cd_S32:
            client.state = client.states['32']  # S32 is the new state
        if is_cd_S33:
            client.state = client.states['33']  # S33 is the new state
        if is_cd_S34:
            client.state = client.states['34']  # S34 is the new state
        if is_cd_S35:
            client.state = client.states['35']  # S36 is the new state
        if is_cd_S36:
            client.state = client.states['36']  # S36 is the new state
        if is_cd_S37:
            client.state = client.states['37']  # S38 is the new state
            
        if is_cd_S31 or is_cd_S32 or is_cd_S33 or is_cd_S34 or is_cd_S35 or \
                is_cd_S36 or is_cd_S37:
            # Schedule an execution of the new state
            client.loop.run_in_executor(None, client.state.do, client, data)
        else:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(
                client.exception_handler, Exception('S3 protocol error'))

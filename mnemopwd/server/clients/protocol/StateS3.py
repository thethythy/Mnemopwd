# -*- coding: utf-8 -*-

# Copyright (C) 2015 Thierry Lemeunier <thierry at lemeunier dot net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
State S3 : Configuration or Data
"""

from server.util.funcutils import singleton

@singleton
class StateS3():
    """State S3 : select Configuration substate (S31) or Data substate (S32) """
        
    def do(self, client, data):
        """Action of the state S3: select substate S31 or S32"""
        
        is_cd_S31 = data[170:183] == b"CONFIGURATION" # Test for S31 substate
        is_cd_S321 = data[170:180] == b"SEARCHDATA" # Test for S321 substate
        is_cd_S322 = data[170:180] == b"CREATEDATA" # Test for S322 substate
        is_cd_S323 = data[170:180] == b"DELETEDATA" # Test for S323 substate
        
        if is_cd_S31 :
            client.state = client.states['31'] # S31 is the new state
        if is_cd_S321 :
            client.state = client.states['321'] # S321 is the new state
        if is_cd_S322 :
            client.state = client.states['322'] # S322 is the new state
        if is_cd_S323 :
            client.state = client.states['323'] # S323 is the new state

        if is_cd_S31 or is_cd_S321 or is_cd_S322 or is_cd_S323 :
            # Schedule an execuction of the new state
            client.loop.run_in_executor(None, client.state.do, client, data)
        else:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, Exception('Protocol error'))

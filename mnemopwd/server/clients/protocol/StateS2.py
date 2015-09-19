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
State S2 : Configuration or Data
"""

from server.util.funcutils import singleton

@singleton
class StateS2():
    """State S2 : select Configuration substate (S21) or Data substate (S22) """
    
    #def __init__(self, client_handler):
    #    """Initialize object"""
    #    ProtocolState.__init__(self, client_handler)
        
    def do(self, client, data):
        """Action of the state S2: select substate S21 or S22"""
        
        is_cd_S21 = data[:13] == b"CONFIGURATION" # Test for S21 substate
        is_cd_S221 = data[:10] == b"SEARCHDATA" # Test for S221 substate
        is_cd_S222 = data[:10] == b"CREATEDATA" # Test for S222 substate
        is_cd_S223 = data[:10] == b"DELETEDATA" # Test for S223 substate
        
        if is_cd_S21 :
            client.state = client.states['21'] # S21 is the new state
        if is_cd_S221 :
            client.state = client.states['221'] # S221 is the new state
        if is_cd_S222 :
            client.state = client.states['222'] # S222 is the new state
        if is_cd_S223 :
            client.state = client.states['223'] # S223 is the new state

        if is_cd_S21 or is_cd_S221 or is_cd_S222 or is_cd_S223 :
            # Schedule an execuction of the new state
            client.loop.run_in_executor(None, client.state.do, client, data)
        else:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, Exception('Protocol error'))

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
State S1 : CountCreation or Login
"""

from server.util.funcutils import singleton

@singleton
class StateS1():
    """State S1 : CountCreation or Login substates"""
    
    #def __init__(self, client_handler):
    #    """Initialize object"""
    #    ProtocolState.__init__(self, client_handler)
        
    def do(self, client, data):
        """Action of the state S1: select substate S11 or S12"""
        
        is_cd_S11 = data[:8] == b"CREATION" # Test for S11 substate
        is_cd_S12 = data[:6] == b"LOGIN" # Test for S12 substate
        
        if is_cd_S11 :
            client.state = client.states['11'] # S11 is the new state
        if is_cd_S12 :
            client.state = client.states['12'] # S12 is the new state

        if is_cd_S11 or is_cd_S12 :
            # Schedule an execuction of the new state
            client.loop.run_in_executor(None, client.state.do, client, data)
        else:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, Exception('Protocol error'))
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
State S11 : CountCreation
"""

from server.util.funcutils import singleton

@singleton
class StateS11():
    """State S11 : CountCreation"""
    
    #def __init__(self, client_handler):
    #    """Initialize object"""
    #    ProtocolState.__init__(self, client_handler)
        
    def do(self, client, data):
        """Action of the state S11: create an id and store it"""
        try:
            print('toto')
        except Exception as exc:
            client.exception_handler(exc)
        else:
            client.state = client.states['12'] # Next state

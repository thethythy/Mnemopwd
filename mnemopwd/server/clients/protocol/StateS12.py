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
State S12 : Login
"""

from server.util.funcutils import singleton
from server.util.funcutils import compute_client_id, compute_client_filename
from server.clients.DBHandler import DBHandler

@singleton
class StateS12():
    """State S12 : Login"""
        
    def do(self, client, data):
        """Action of the state S12: control client login and id"""
        try:
            
            is_cd_S12 = data[:5] == b"LOGIN" # Test for S12 command
            
            if not is_cd_S12 :
                raise Exception('Protocol error')
                
            eid = data[6:175]   # id encrypted
            ems = data[176:377] # Master secret encrypted
            elogin = data[378:] # Login encrypted 

            # Compute client id
            id, ms, login = compute_client_id(client, ems, elogin)
            
            # Get id from client
            id_from_client = client.ephecc.decrypt(eid)
            
            # Test if login exists
            filename = compute_client_filename(id, ms, login)
            exist = DBHandler.exist(client.db_path, filename)
            
            # If login is OK and ids are equal
            if exist and id == id_from_client :
                client.dbhandler = DBHandler(client.db_path, filename)
                client.state = client.states['2']
                client.transport.write(b'OK')
            
            # If login is OK but ids are not equal
            elif exist and id != id_from_client :
                client.transport.write(b'ERROR;' + b'wrong id')
                raise Exception('Good login but bad id')
                
            # If login is unknown
            elif not exist :
                client.state = client.states['11']
                client.transport.write(b'ERROR;' + b'login does not exist')
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

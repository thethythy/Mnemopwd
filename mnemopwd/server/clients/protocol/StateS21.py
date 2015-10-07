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
State S21 : Login
"""

from server.util.funcutils import singleton
from server.clients.protocol.StateSCC import StateSCC
from server.clients.DBHandler import DBHandler

@singleton
class StateS21(StateSCC):
    """State S21 : Login"""
        
    def do(self, client, data):
        """Action of the state S21: control client login and id"""
        try:
            
            # Control challenge
            if self.control_challenge(client, data, b'S21.7') :
            
                # Test for S21 command
                is_cd_S21 = data[170:175] == b"LOGIN"
                if not is_cd_S21 : raise Exception('protocol error')
                
                eid = data[176:345]   # id encrypted
                elogin = data[346:] # Login encrypted

                # Compute client id
                login = client.ephecc.decrypt(elogin)
                id = self.compute_client_id(client.ms, login)
                        
                # Get id from client
                id_from_client = client.ephecc.decrypt(eid)
            
                # If ids are not equal
                if id != id_from_client :
                    client.transport.write(b'ERROR;' + b'incorrect id')
                    raise Exception('incorrect id')
            
                # Test if login exists
                filename = self.compute_client_filename(id, client.ms, login)
                exist = DBHandler.exist(client.db_path, filename)
            
                # If login is OK and ids are equal
                if id == id_from_client and exist :
                    client.dbhandler = DBHandler(client.db_path, filename)
                    client.transport.write(b'OK')
                    client.state = client.states['3']
                
                # If login is unknown
                elif id == id_from_client and not exist :
                    client.transport.write(b'ERROR;' + b'count does not exist')
                    raise Exception('count does not exist')
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

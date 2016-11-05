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
State S33 : Deletion
"""

import logging

from ...util.funcutils import singleton
from .StateSCC import StateSCC
from ..DBHandler import DBHandler


@singleton
class StateS33(StateSCC):
    """State S33 : Deletion"""

    def do(self, client, data):
        """Action of the state S33: delete a user account"""

        try:
            # Control challenge
            if self.control_challenge(client, data, b'S33.7'):

                # Test for S33 command
                is_cd_S33 = data[170:178] == b"DELETION"
                if not is_cd_S33:
                    raise Exception('S33 protocol error')

                eid = data[179:348]  # id encrypted
                elogin = data[349:]  # Login encrypted

                # Compute client id
                login = client.ephecc.decrypt(elogin)
                id = self.compute_client_id(client.ms, login)

                # Get id from client
                id_from_client = client.ephecc.decrypt(eid)

                # If ids are not equal
                if id != id_from_client:
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('incorrect id')

                # Test if login exists
                filename = self.compute_client_filename(id, client.ms, login)
                exist = DBHandler.exist(client.dbpath, filename)

                # If login is unknown
                if not exist:
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('user account does not exist')

                logging.info('User account deletion request from {}'
                             .format(client.peername))

                # If login is OK try to delete database file
                result = DBHandler.delete(client.dbpath, filename)

                # If database file has been deleted close connection with client
                if result:
                    client.loop.call_soon_threadsafe(
                        client.transport.write, b'OK')
                    client.loop.call_soon_threadsafe(client.transport.close)
                    logging.warning('User account {} deletion from {}'
                                    .format(filename, client.peername))

                # If deletion has failed for some reason
                else:
                    msg = b'ERROR;application protocol error'
                    client.loop.call_soon_threadsafe(client.transport.write, msg)
                    raise Exception('deletion rejected')

        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)

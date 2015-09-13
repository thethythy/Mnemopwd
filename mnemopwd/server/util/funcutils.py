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

# ---------------------------------------------------------
# Singleton class

import hashlib
import base64
from pyelliptic.hash import hmac_sha512

def singleton(the_class):
    instances = {} # Dictionary of singleton objects
    def get_instance():
        if the_class not in instances:
            instances[the_class] = the_class() # Create a singleton object and store it
        return instances[the_class]
    return get_instance

# ---------------------------------------------------------
# Compute client id

def compute_client_id(client, ems, elogin):
    """Compute a client id according to the protocol"""
    ms = client.ephecc.decrypt(ems)         # Decrypt master secret
    login = client.ephecc.decrypt(elogin)   # Decrypt login
                
    # Compute client id
    ho = hashlib.sha256()
    ho.update(hmac_sha512(ms, ms + login))
    return base64.b64encode(ho.digest())

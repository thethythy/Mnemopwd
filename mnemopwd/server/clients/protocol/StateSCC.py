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
State SCC : Challenge Controller
"""

import hashlib
import base64

from ....pyelliptic import hmac_sha512
from ....pyelliptic import hmac_sha256


class StateSCC:
    """Challenge controller and others useful methods"""
    
    def control_challenge(self, client, data, var):
        """Action of the state SCC: control the challenge answer"""
        
        try:
            echallenge = data[:169]  # Encrypted challenge
            challenge = client.ephecc.decrypt(echallenge)  # Decrypting
            
            # Compute challenge
            challenge_bis = hmac_sha256(client.ms, client.session + var)
            
            if challenge != challenge_bis:
                # Send challenge rejected
                msg = b'ERROR;application protocol error'
                client.loop.call_soon_threadsafe(client.transport.write, msg)
                raise Exception(var.decode() + " challenge rejected")
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            client.loop.call_soon_threadsafe(client.exception_handler, exc)
            return False
        
        else:
            return True

    def compute_client_id(self, ms, login):
        """Compute a client id"""
        ho = hashlib.sha256()
        ho.update(hmac_sha512(ms, ms + login))
        return ho.digest()

    def compute_client_filename(self, id, ms, login):
        """Compute a client database filename"""
    
        # Compute login hash
        ho = hashlib.sha256()
        ho.update(hmac_sha512(ms, login))
        hlogin = ho.digest()
    
        # Filename construction
        filename = (base64.b32encode(hlogin))[:52] + (base64.b32encode(id))[:52]
    
        return filename.decode()  # Return client database filename (a string)

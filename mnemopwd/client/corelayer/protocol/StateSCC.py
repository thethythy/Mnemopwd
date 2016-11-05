# -*- coding: utf-8 -*-

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
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
State SCC : Challenge Creation
"""

import hashlib

from ....pyelliptic import hmac_sha256
from ....pyelliptic import hmac_sha512


class StateSCC:
    """Challenge creation and others useful methods"""
    
    def compute_challenge(self, handler, var):
        """Create the challenge answer"""
        try:
            # Compute challenge then encrypt it
            challenge = hmac_sha256(handler.ms, handler.session + var)
            echallenge = handler.ephecc.encrypt(
                challenge, pubkey=handler.ephecc.get_pubkey())
            
        except Exception as exc:
            # Schedule a callback to client exception handler
            handler.loop.call_soon_threadsafe(handler.exception_handler, exc)
            return False
        
        else:
            return echallenge

    def compute_client_id(self, ms, login):
        """Compute a client id"""
        ho = hashlib.sha256()
        ho.update(hmac_sha512(ms, ms + login))
        return ho.digest()

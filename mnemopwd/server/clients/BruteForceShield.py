# -*- coding: utf-8 -*-

# Copyright (c) 2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
Protection against brute force attack attempts via "login" functionality and
"user account creation" functionality.

It consists on client IP filtering after a maximum of attempts. For example,
after 3 login attempts from a same client IP, this IP is temporarily banished
during one hour.
"""

import time
import logging

from ..util.Configuration import Configuration


class BruteForceShield:
    """Brute-force attack shield"""

    banishment_period = 3600  # One hour of banishment

    def __init__(self):
        """Object initialization"""
        self.shield = dict()  # IP hashtable

    def _close_banishment(self, ip):
        """Rehabilitate an IP banished"""
        del self.shield[ip]  # Banishment is finished
        logging.critical('IP {} is now rehabilitated'.format(ip))

    def _ip_rehabilitation(self):
        """IP hashtable update"""
        to_rehabilitate = list()
        for key in self.shield.keys():
            counter, start_time = self.shield[key]
            duration = time.time() - start_time
            if duration > BruteForceShield.banishment_period:
                to_rehabilitate.append(key)
        for ip in to_rehabilitate:
            self._close_banishment(ip)

    def add_suspect_ip(self, ip):
        """Try do add a suspect IP"""
        try:
            counter, start_time = self.shield[ip]  # Try to get the suspect IP

            self.shield[ip] = (1 + counter, start_time)
            if (1 + counter) == (1 + Configuration.max_login):
                logging.critical('IP {} is now temporarily banished'.format(ip))

        except KeyError:
            self.shield[ip] = (1, time.time())  # IP does not exist
            logging.critical('IP {} is now considered as suspect'.format(ip))

    def is_suspect_ip(self, ip, loop):
        """Test if the given argument is a suspect IP.
        Return False if not, otherwise return True"""
        try:
            counter, start_time = self.shield[ip]  # This IP already exists ?

            # This IP is suspect. Check if banishment period is over
            duration = time.time() - start_time
            if duration > BruteForceShield.banishment_period:
                self._close_banishment(ip)
                return False
            else:
                return counter > Configuration.max_login  # Check max attempts

        except KeyError:
            return False  # Not a suspect IP

        finally:
            # Schedule a table update
            loop.run_in_executor(None, self._ip_rehabilitation)

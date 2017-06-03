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
IP configuration of the client
"""

import socket
from ipaddress import ip_address, ip_network
import threading


class IPConfiguration:
    """IP configuration of the client"""

    private_networks = ["192.168.0.0/16", "172.16.0.0/12", "10.0.0.0/8"]
    deflt_ip = "127.0.0.1"
    deflt_port = 62230
    stop = False

    @staticmethod
    def get_host_ip_address():
        """Get the host IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('123.123.123.123', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    @staticmethod
    def test_ip_address(ip, port):
        """Test an address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        try:
            s.connect((ip, port))
            return True
        except socket.timeout:
            return False
        except ConnectionRefusedError:
            return False
        except PermissionError:
            return False
        finally:
            s.close()

    @staticmethod
    def stop_searching():
        """Stop searching"""
        IPConfiguration.stop = True

    @staticmethod
    def found(timer, ip, port):
        """A server has been found"""
        timer.cancel()
        print('Server found at ' + ip + ':' + str(port))
        return ip, port

    @staticmethod
    def abort(timer, msg):
        """Server has not been found"""
        timer.cancel()
        print(msg)
        print('Use option -i on the command line to specify IP MnemoPwd server.')
        exit(1)

    @staticmethod
    def find_server_address(ip, port):
        """Find the ip and the connection port of the Mnemopwd server"""
        try:
            print("Searching MnemoPwd server...")

            if ip is None:
                ip = IPConfiguration.deflt_ip
            if port is None:
                port = IPConfiguration.deflt_port

            # Always stop after 5 minutes
            timer = threading.Timer(5 * 60, IPConfiguration.stop_searching)
            timer.start()

            # First: try 4 simple combinations
            for sip, sport in [(ip, port), (ip, IPConfiguration.deflt_port),
                               (IPConfiguration.deflt_ip, port),
                               (IPConfiguration.deflt_ip,
                                IPConfiguration.deflt_port)]:
                if IPConfiguration.test_ip_address(sip, sport):
                    return IPConfiguration.found(timer, sip, sport)

            # Second: search in the local network
            host_ip = IPConfiguration.get_host_ip_address()
            for net in IPConfiguration.private_networks:
                if ip_address(host_ip) in ip_network(net):
                    for sip in ip_network(net).hosts():
                        # Look at the given port
                        if IPConfiguration.test_ip_address(sip.exploded, port):
                            return IPConfiguration.found(timer, sip.exploded,
                                                         port)

                        # Look at the default port
                        if port != IPConfiguration.deflt_port:
                            if IPConfiguration.test_ip_address(
                                    sip.exploded,
                                    IPConfiguration.deflt_port):
                                return IPConfiguration.found(timer,
                                                             sip.exploded,
                                                             IPConfiguration.deflt_port)

                        # Search timed out
                        if IPConfiguration.stop:
                            IPConfiguration.abort(timer,
                                                  'Enable to find a MnemoPwd server after 5 minutes.')

            # At this point, you know the LAN is not a normal private network
            IPConfiguration.abort(timer,
                                  'Your local network is not conform to RFC 1918.')

        except KeyboardInterrupt:
            IPConfiguration.abort(timer,
                                  'Waited enough? Enable to find a MnemoPwd server.')

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
Configuration of the client

The priority (from low to high) for loading configuration values is :
- the default builtin values
- the configuration file values
- the command line values
"""

import logging
import configparser
import argparse
import os.path
import os
import stat
import json

from common.util.X509 import X509

class MyParserAction(argparse.Action):
    """Actions for command line parser"""
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(MyParserAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-c', '--cert'] :
            Configuration.certfile = values
        if option_string in ['-i', '--ip'] :
            Configuration.server = values
        if option_string in ['-p', '--port'] :
            if values in range(Configuration.port_min, Configuration.port_max):
                Configuration.port = int(values)
            else:
                parser.error("argument -p/--port: invalid choice: {} (choose between {} and {})"\
                             .format(values, Configuration.port_min, Configuration.port_max))

class Configuration:
    """Configuration of the server"""

    configfile = os.path.expanduser('~') + '/.mnemopwdc' # Configuration file
    certfile = 'None'       # Default certificat X509 file
    version = '1.0'         # Client version
    server = '127.0.0.1'    # Default server IP
    port = 62230            # Default server port
    port_min = 49152        # Minimum port value
    port_max = 65535        # Maximum port value
    loglevel = 'DEBUG'      # Default logging level
    poolsize = 1            # Pool executor size
    queuesize = 500         # Queue size: up to 500 commands can be scheduled
    curve1 = 'sect571r1'    # Curve name for the first stage
    cipher1 = 'aes-256-cbc' # Cipher name for the first stage
    curve2 = 'None'         # Curve name for the second stage
    cipher2 = 'None'        # Cipher name for the second stage
    curve3 = 'None'         # Curve name for the third stage
    cipher3 = 'None'        # Cipher name for the third stage
    action = 'start'        # Default action if not given
    timeout = 5             # Timeout on connection request

    @staticmethod
    def __test_cert_file__(parser, certfile):
        """Test existence and permissions of certificat file"""
        if not os.path.exists(certfile) :
            parser.error("invalid certificat file {} (it not exists)".format(certfile))
        return True

    @staticmethod
    def __test_config_file__(parser, path):
        """Test existence and permissions of configuration file"""
        if not os.path.exists(path) :
            return False
        else:
            statinfo = os.stat(path)
            if not os.path.isfile(path) or os.path.islink(path):
                parser.error("invalid configuration file {} (it must be a regular file)".format(path))
            elif stat.filemode(statinfo.st_mode) != '-rw-------' :
                parser.error("invalid configuration file {} (it must have only read and write permissions for user)".format(path))
            elif statinfo.st_uid != os.getuid() :
                parser.error("invalid configuration file {} (the owner must be the user)".format(path))
        return True

    @staticmethod
    def __load_config_file__(parser, fileparser):
        """Load configuration file"""
        try:
            fileparser.read(Configuration.configfile)
        except:
            parser.error("parsing error of configuration file {}".format(Configuration.configfile))
        else:
            Configuration.server = fileparser['server']['server']
            Configuration.port = int(fileparser['server']['port'])
            Configuration.certfile = fileparser['server']['certfile']
            Configuration.timeout = int(fileparser['server']['timeout'])

            def testNone(name):
                if name == 'None': return ""
                else: return name
            Configuration.curve1 = testNone(fileparser['client']['curve1'])
            Configuration.cipher1 = testNone(fileparser['client']['cipher1'])
            Configuration.curve2 = testNone(fileparser['client']['curve2'])
            Configuration.cipher2 = testNone(fileparser['client']['cipher2'])
            Configuration.curve3 = testNone(fileparser['client']['curve3'])
            Configuration.cipher3 = testNone(fileparser['client']['cipher3'])

    @staticmethod
    def __create_config_file__(fileparser):
        """Method to create default configuration file"""
        fileparser['server'] = {'server': Configuration.server + " # Server IP", \
                                'port': str(Configuration.port) \
                                        + " # Values allowed: " + str(Configuration.port_min) \
                                        + ".." + str(Configuration.port_max), \
                                'certfile': Configuration.certfile + " # Use an absolute path", \
                                'timeout': str(Configuration.timeout) + " # Timeout on connection request"}
        fileparser['client'] = {'curve1': Configuration.curve1 + " # Values allowed: ...", \
                                'cipher1': Configuration.cipher1 + " # Values allowed: ...", \
                                'curve2': Configuration.curve2 + " # Values allowed: None ...", \
                                'cipher2': Configuration.cipher2 + " # Values allowed: None ...", \
                                'curve3': Configuration.curve3 + " # Values allowed: None ...", \
                                'cipher3': Configuration.cipher3 + " # Values allowed: None ..."}
        with open(Configuration.configfile, 'w') as configfile:
            fileparser.write(configfile)
        os.chmod(Configuration.configfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)

    @staticmethod
    def configure():
        """Configure the server: load configuration file then parse command line"""

        # Create and configure a command line parser
        argparser = argparse.ArgumentParser(description='MnemoPwd client v' + Configuration.version, \
                                            epilog='More informations can be found at https://github.com/thethythy/Mnemopwd', \
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # IP server
        argparser.add_argument('-i', '--ip', nargs='?', default=Configuration.server, \
                               metavar='ip', help='the IP address of the server', \
                               action=MyParserAction)

        # Port
        argparser.add_argument('-p', '--port' , type=int, nargs='?', default=Configuration.port, \
                               metavar='port', help='the server connexion port', \
                               action=MyParserAction)

        # Certificat file
        argparser.add_argument('-c', '--cert', nargs='?', default=Configuration.certfile, \
                               metavar='certificat', type=str, help="the server PEM X509 \
                               certificat file", action=MyParserAction)

        # Start action
        argparser.add_argument('--start', action='store_const', const='start', dest='action', \
                               default=Configuration.action, help='start the client')

        # Status action
        argparser.add_argument('--status', action='store_const', const='status', dest='action', \
                               default=Configuration.action, help='get server status')

        # Program version
        argparser.add_argument('-v', '--version', action='version', version='version ' \
                               + Configuration.version)

        # Create, configure a configuration file parser and parse
        fileparser = configparser.ConfigParser(inline_comment_prefixes='#')
        if Configuration.__test_config_file__(argparser, Configuration.configfile) :
            # Load values from configuration file
            Configuration.__load_config_file__(argparser, fileparser)
            Configuration.first_execution = False
        else:
            # Create default configuration file
            Configuration.__create_config_file__(fileparser)
            Configuration.first_execution = True

        # Parse the command line to get options
        options = argparser.parse_args()
        Configuration.action = options.action # Action to apply to the server

        # Verify certificat file
        if Configuration.certfile != 'None' :
            Configuration.__test_cert_file__(argparser, Configuration.certfile)
            try:
                X509(Configuration.certfile).check_validity_period() # Control validity period
            except Exception as e :
                print(e)
                exit(1)

        # Load SIB types
        with open('client/util/blocktypes.json', 'rt') as jsonfile:
            Configuration.btypes = json.load(jsonfile)

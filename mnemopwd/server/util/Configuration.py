# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017, Thierry Lemeunier <thierry at lemeunier dot net>
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
Configuration of the server

The priority (from low to high) for loading configuration values is :
- the default builtin values
- the configuration file values
- the command line values
"""

import configparser
import argparse
import os.path
import os
import stat

import mnemopwd
from ...common.util.X509 import X509
from .funcutils import getIPAddress


class MyParserAction(argparse.Action):
    """Actions for command line parser"""

    def __init__(self, option_strings, dest, **kwargs):
        super(MyParserAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-m', '--searchmode']:
            Configuration.search_mode = values
        if option_string in ['-s', '--poolsize']:
            Configuration.poolsize = values
        if option_string in ['-d', '--dbpath']:
            Configuration.dbpath = values
        if option_string in ['-c', '--cert']:
            Configuration.certfile = values
        if option_string in ['-k', '--key']:
            Configuration.keyfile = values
        if option_string in ['-i', '--ip']:
            Configuration.host = values
        if option_string in ['-p', '--port']:
            if values in range(Configuration.port_min, Configuration.port_max):
                Configuration.port = int(values)
            else:
                parser.error("argument -p/--port: invalid choice: {} (choose between {} and {})"
                             .format(values, Configuration.port_min, Configuration.port_max))


class Configuration:
    """Configuration of the server"""

    configfile = os.path.expanduser('~') + '/.mnemopwds'  # Configuration file
    dbpath = os.path.expanduser('~') + '/mnemopwddata'  # Default database path
    pidfile = os.path.expanduser('~') + '/mnemopwddata/mnemopwds.pid'  # Default daemon pid file
    logfile = os.path.expanduser('~') + '/mnemopwddata/mnemopwds.log'  # Default log file
    certfile = 'None'  # Default certificate X509 file
    keyfile = 'None'  # Default certificate private key file
    logmaxmb = 1  # Default logfile volume (1 => 1 MBytes)
    logbackups = 20  # Default backup logfile
    loglevel = 'INFO'  # Default logging level
    version = mnemopwd.__version__  # Server version
    host = getIPAddress()  # Default host
    port = 62230  # Default port
    port_min = 49152  # Minimum port value
    port_max = 65535  # Maximum port value
    poolsize = 10  # Default pool executor size
    search_mode = 'all'  # Default search mode
    max_login = 5  # Default maximum login attempts per hour
    action = 'status'  # Default action if not given

    @staticmethod
    def __test_cert_key_files__(parser, certfile, keyfile):
        """Test existence and permissions of private key file"""
        if not os.path.exists(keyfile):
            parser.error("invalid key file {} (it not exists)".format(keyfile))
        elif not os.path.exists(certfile):
            parser.error("invalid certificate file {} (it not exists)".
                         format(certfile))
        else:
            statinfo = os.stat(keyfile)
            if certfile == keyfile:
                parser.error(
                    "the certificate file ({}) and the key file ({}) must be different"
                    .format(certfile, keyfile))
            if stat.filemode(statinfo.st_mode) != '-rw-------':
                parser.error(
                    "invalid key file {} (it must have only read, write and execution permissions for user)"
                    .format(keyfile))
            elif statinfo.st_uid != os.getuid():
                parser.error("invalid key file {} (the owner must be the user)".
                             format(keyfile))
        return True

    @staticmethod
    def __test_dbpath__(parser, path):
        """Test existence and permissions of database directory"""
        if not os.path.exists(path):
            os.mkdir(path, mode=0o700)
        else:
            statinfo = os.stat(path)
            if not os.path.isdir(path) or os.path.islink(path):
                parser.error("invalid database path {} (it must be a directory)".format(path))
            elif stat.filemode(statinfo.st_mode) != 'drwx------':
                parser.error(
                    "invalid database path {} (it must have only read, write and execution permissions for user)"
                    .format(path))
            elif statinfo.st_uid != os.getuid():
                parser.error(
                    "invalid database path {} (the owner must be the user)"
                    .format(path))
        return True

    @staticmethod
    def __test_config_file__(parser, path):
        """Test existence and permissions of configuration file"""
        if not os.path.exists(path):
            return False
        else:
            statinfo = os.stat(path)
            if not os.path.isfile(path) or os.path.islink(path):
                parser.error(
                    "invalid configuration file {} (it must be a regular file)"
                    .format(path))
            elif stat.filemode(statinfo.st_mode) != '-rw-------':
                parser.error(
                    "invalid configuration file {} (it must have only read and write permissions for user)"
                    .format(path))
            elif statinfo.st_uid != os.getuid():
                parser.error(
                    "invalid configuration file {} (the owner must be the user)"
                    .format(path))
        return True

    @staticmethod
    def __load_config_file__(parser, fileparser):
        """Load configuration file"""
        try:
            fileparser.read(Configuration.configfile)
        except configparser.ParsingError:
            parser.error("parsing error of configuration file {}"
                         .format(Configuration.configfile))
        else:
            Configuration.port = int(fileparser['server']['port'])
            Configuration.host = fileparser['server']['host']
            Configuration.dbpath = fileparser['server']['dbpath']
            Configuration.certfile = fileparser['server']['certfile']
            Configuration.keyfile = fileparser['server']['keyfile']
            Configuration.poolsize = int(fileparser['server']['poolsize'])
            Configuration.search_mode = fileparser['server']['search_mode']
            Configuration.loglevel = fileparser['server']['loglevel']
            Configuration.max_login = int(fileparser['server']['max_login'])
            Configuration.pidfile = fileparser['daemon']['pidfile']
            Configuration.logfile = fileparser['daemon']['logfile']
            Configuration.logmaxmb = int(fileparser['daemon']['logmaxmb'])
            Configuration.logbackups = int(fileparser['daemon']['logbackups'])

    @staticmethod
    def __create_config_file__(fileparser):
        """Method to create default configuration file"""
        fileparser['server'] = {
            'port': str(Configuration.port) + " # Values allowed: "
            + str(Configuration.port_min)
            + "..." + str(Configuration.port_max),
            'host': Configuration.host + " # IP server",
            'dbpath': Configuration.dbpath + " # Use an absolute path",
            'certfile': Configuration.certfile + " # Use an absolute path",
            'keyfile': Configuration.keyfile + " # Use an absolute path",
            'poolsize': str(Configuration.poolsize) + " # Number of thread",
            'search_mode': Configuration.search_mode
            + " # Values allowed: all first",
            'loglevel': Configuration.loglevel
            + " # Values allowed: DEBUG INFO WARNING ERROR CRITICAL",
            'max_login': str(Configuration.max_login)
            + " # Maximum login attempt per hour"
        }
        fileparser['daemon'] = {
            'pidfile': Configuration.pidfile + " # Use an absolute path",
            'logfile': Configuration.logfile + " # Use an absolute path",
            'logmaxmb': str(Configuration.logmaxmb)
            + " # Maximum size of log file in MBytes",
            'logbackups': str(Configuration.logbackups)
            + " # Number of backup log files"
        }
        with open(Configuration.configfile, 'w') as configfile:
            fileparser.write(configfile)
        os.chmod(Configuration.configfile,
                 stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)

    @staticmethod
    def configure():
        """
        Configure the server: load configuration file then parse command line
        """

        # Create and configure a command line parser
        argparser = argparse.ArgumentParser(
            description='MnemoPwd server v' + Configuration.version,
            epilog='More information can be found at https://github.com/thethythy/Mnemopwd',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # IP server
        argparser.add_argument(
            '-i', '--ip', nargs='?', default=Configuration.host, metavar='ip',
            help='the IP address of the server', action=MyParserAction)

        # Port
        argparser.add_argument(
            '-p', '--port', type=int, nargs='?', default=Configuration.port,
            metavar='port', help='the server connexion port',
            action=MyParserAction)

        # Database directory
        argparser.add_argument(
            '-d', '--dbpath', nargs='?', default=Configuration.dbpath,
            metavar='path', type=str, help="the directory to store secret data; \
            it will be created if it does not exist; if the directory already \
            exists only the user must have read, write and execution permissions",
            action=MyParserAction)

        # Certificat file
        argparser.add_argument(
            '-c', '--cert', nargs='?', default=Configuration.certfile,
            metavar='certificate', type=str, help="the PEM X509 certificate file",
            action=MyParserAction)

        # Certificat private key file
        argparser.add_argument(
            '-k', '--key', nargs='?', default=Configuration.keyfile,
            metavar='private_key', type=str, help="the private key file \
            to authenticate the certificate", action=MyParserAction)

        # Pool executor size
        argparser.add_argument(
            '-s', '--poolsize', type=int, default=Configuration.poolsize,
            metavar='pool_size', help="the size of the pool of execution",
            action=MyParserAction)

        # Search mode
        argparser.add_argument(
            '-m', '--searchmode', type=str, default=Configuration.search_mode,
            metavar='search_mode', help="the search mode; 'first' for \
            searching only on first secret information block and 'all' \
            for searching on all information", action=MyParserAction)

        # Start action
        argparser.add_argument(
            '--start', action='store_const', const='start', dest='action',
            default=Configuration.action, help='start the server')

        # Stop action
        argparser.add_argument(
            '--stop', action='store_const', const='stop', dest='action',
            default=Configuration.action, help='stop the server')

        # Status action
        argparser.add_argument(
            '--status', action='store_const', const='status', dest='action',
            default=Configuration.action, help='get server status')

        # Program version
        argparser.add_argument(
            '-v', '--version', action='version',
            version='version ' + Configuration.version)

        # Create, configure a configuration file parser and parse
        fileparser = configparser.ConfigParser(inline_comment_prefixes='#')
        if Configuration.__test_config_file__(
                argparser, Configuration.configfile):
            # Load values from configuration file
            Configuration.__load_config_file__(argparser, fileparser)
        else:
            # Create default configuration file
            Configuration.__create_config_file__(fileparser)

        # Parse the command line to get options
        options = argparser.parse_args()
        Configuration.action = options.action  # Action to apply to the server

        # Verify dbpath
        Configuration.__test_dbpath__(argparser, Configuration.dbpath)

        # Verify private key and certificate files
        if Configuration.keyfile != 'None' and Configuration.certfile != 'None':
            Configuration.__test_cert_key_files__(
                argparser, Configuration.certfile, Configuration.keyfile)
            try:
                # Control validity period
                X509(Configuration.certfile).check_validity_period()
            except Exception as e:
                print(e)
                exit(1)
        elif (Configuration.keyfile != 'None' and
                Configuration.certfile == 'None') or \
             (Configuration.keyfile == 'None' and
                Configuration.certfile != 'None'):
            argparser.error(
                "give two files (certificate file and key file) or nothing")

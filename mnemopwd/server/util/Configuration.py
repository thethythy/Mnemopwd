# -*- coding: utf-8 -*-

# Copyright (c) 2015, Thierry Lemeunier <thierry at lemeunier dot net>
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

import logging
import configparser
import argparse
import os.path
import os
import stat

class MyParserAction(argparse.Action):
    """Actions for command line parser"""
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(MyParserAction, self).__init__(option_strings, dest, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-m', '--searchmode'] :
            Configuration.search_mode = values
        if option_string in ['-s', '--poolsize'] :
            Configuration.poolsize = values
        if option_string in ['-d', '--dbpath'] :
            Configuration.dbpath = values
        if option_string in ['-p', '--port'] :
            if values in range(Configuration.port_min, Configuration.port_max):
                Configuration.port = int(values)
            else:
                parser.error("argument -p/--port: invalid choice: {} (choose between {} and {})"\
                             .format(values, Configuration.port_min, Configuration.port_max))

class Configuration:
    """Configuration of the server"""
    
    configfile = os.path.expanduser('~') + '/.mnemopwd' # Configuration file
    dbpath = os.path.expanduser('~') + '/mnemopwddata' # Default database path
    pidfile = os.path.expanduser('~') + '/mnemopwddata/mnemopwds.pid' # Default daemon pid file
    logfile = os.path.expanduser('~') + '/mnemopwddata/mnemopwds.log' # Default log file
    logmaxmb = 1            # Default logfile volume (1 => 1 MBytes)
    logbackups = 20         # Default backup logfile
    loglevel = 'INFO'       # Default logging level
    version = '1.0'         # Server version
    host = '127.0.0.1'      # Default host
    port = 62230            # Default port
    port_min = 49152        # Minimum port value
    port_max = 65535        # Maximum port value
    poolsize = 10           # Default pool executor size
    search_mode = 'first'   # Default search mode
    action = 'status'       # Default action if not given
    
    @staticmethod
    def __test_dbpath__(path):
        """Test existence and permissions of database directory"""
        if not os.path.exists(path):
            os.mkdir(path, mode=0o700)
        else:
            statinfo = os.stat(path)
            if not os.path.isdir(path) or os.path.islink(path):
                logging.critical("Error: invalid database path {} (it must be a directory)".format(path))
                exit(2)
            elif stat.filemode(statinfo.st_mode) != 'drwx------' :
                logging.critical("Error: invalid database path {} (it must have only read, write and excecution permissions for user)".format(path))
                exit(2)
            elif statinfo.st_uid != os.getuid() :
                logging.critical("Error: invalid database path {} (the owner must be the user)".format(path))
                exit(2)
        return True
    
    @staticmethod
    def __test_config_file__(path):
        """Test existence and permissions of configuration file"""
        if not os.path.exists(path) :
            return False
        else:
            statinfo = os.stat(path)
            if not os.path.isfile(path) or os.path.islink(path):
                logging.critical("Error: invalid configuration file {} (it must be a regular file)".format(path))
                exit(2)
            elif stat.filemode(statinfo.st_mode) != '-rw-------' :
                logging.critical("Error: invalid configuration file {} (it must have only read and write permissions for user)".format(path))
                exit(2)
            elif statinfo.st_uid != os.getuid() :
                logging.critical("Error: invalid configuration file {} (the owner must be the user)".format(path))
                exit(2)
        return True
            
    @staticmethod
    def __load_config_file__(fileparser):
        """Load configuration file"""
        try:
            fileparser.read(Configuration.configfile)
        except:
            logging.critical("Error: parsing error of configuration file {}".format(Configuration.configfile))
            exit(2)
        else:
            Configuration.port = int(fileparser['server']['port'])
            Configuration.dbpath = fileparser['server']['dbpath']
            Configuration.poolsize = int(fileparser['server']['poolsize'])
            Configuration.search_mode = fileparser['server']['search_mode']
            Configuration.loglevel = fileparser['server']['loglevel']
            Configuration.pidfile = fileparser['daemon']['pidfile']
            Configuration.logfile = fileparser['daemon']['logfile']
            Configuration.logmaxmb = int(fileparser['daemon']['logmaxmb'])
            Configuration.logbackups = int(fileparser['daemon']['logbackups'])
    
    @staticmethod
    def __create_config_file__(fileparser):
        """Method to create default configuration file"""
        fileparser['server'] = {'port': str(Configuration.port) \
                                        + " # Values allowed: " + str(Configuration.port_min) \
                                        + "..." + str(Configuration.port_max), \
                                'dbpath': Configuration.dbpath + " # Use an absolute path", \
                                'poolsize': str(Configuration.poolsize) + " # Number of thread" , \
                                'search_mode': Configuration.search_mode \
                                               + " # Values allowed: all first", \
                                'loglevel': Configuration.loglevel \
                                            + " # Values allowed: DEBUG INFO WARNING ERROR CRITICAL"}
        fileparser['daemon'] = {'pidfile': Configuration.pidfile + " # Use an absolute path", \
                                'logfile': Configuration.logfile + " # Use an absolute path", \
                                'logmaxmb': str(Configuration.logmaxmb) \
                                            + " # Maximum size of log file in MBytes",\
                                'logbackups': str(Configuration.logbackups) \
                                              +  " # Number of backup log files"}
        with open(Configuration.configfile, 'w') as configfile:
            fileparser.write(configfile)
        os.chmod(Configuration.configfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
    
    @staticmethod
    def configure():
        """Configure the server: load configuration file then parse command line"""
        
        # Create, configure a configuration file parser and parse
        fileparser = configparser.ConfigParser(inline_comment_prefixes='#')
        if Configuration.__test_config_file__(Configuration.configfile) :
            # Load values from configuration file
            Configuration.__load_config_file__(fileparser)
        else:
            # Create default configuration file
            Configuration.__create_config_file__(fileparser)
        
        # Create and configure a command line parser
        argparser = argparse.ArgumentParser(description='MnemoPwd server v' + Configuration.version, \
                                            epilog='More informations can be found at https://github.com/thethythy/Mnemopwd', \
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        # Port
        argparser.add_argument('-p', '--port' , type=int, nargs='?', default=Configuration.port, \
                               metavar='port', help='the server connexion port', \
                               action=MyParserAction)
        # Database directory
        argparser.add_argument('-d', '--dbpath', nargs='?', default=Configuration.dbpath, \
                               metavar='path', type=str, help="the directory to store \
                               secret data; it will be created if it does not exist; \
                               if the directory already exists only the user must \
                               have read, write and execution permissions", \
                               action=MyParserAction)
        # Pool executor size
        argparser.add_argument('-s', '--poolsize', type=int, default=Configuration.poolsize, \
                               metavar='pool_size', help="the size of the pool of execution", \
                               action=MyParserAction)
        # Search mode
        argparser.add_argument('-m', '--searchmode', type=str, default=Configuration.search_mode, \
                               metavar='search_mode', help="the search mode; 'first' for \
                               searching only on first secret information and 'all' for \
                               searching on all informations", action=MyParserAction)
        
        # Start action
        argparser.add_argument('--start', action='store_const', const='start', dest='action', \
                               default=Configuration.action, help='start the server')
        
        # Stop action
        argparser.add_argument('--stop', action='store_const', const='stop', dest='action', \
                               default=Configuration.action, help='stop the server')
        
        # Status action
        argparser.add_argument('--status', action='store_const', const='status', dest='action', \
                               default=Configuration.action, help='get server status')
        
        # Program version
        argparser.add_argument('-v', '--version', action='version', version='version ' + Configuration.version)
        
        options = argparser.parse_args() # Parse the command line
        
        Configuration.action = options.action # Action to apply to the server
        
        # Verify dbpath
        Configuration.__test_dbpath__(Configuration.dbpath)
        
if __name__ == '__main__':
    Configuration.configure()
    print(Configuration.dbpath)
    print(Configuration.port)
    print(Configuration.poolsize)
    print(Configuration.search_mode)

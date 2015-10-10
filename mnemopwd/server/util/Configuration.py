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
    version = '0.1'     # Server version
    host = '127.0.0.1'  # Default host
    port = 62230        # Default port
    port_min = 49152    # Minimum port value
    port_max = 65535    # Maximum port value
    poolsize = 10       # Default pool executor size
    
    @staticmethod
    def __test_dbpath__(path):
        """Test existence and permissions of database directory"""
        if not os.path.exists(path):
            os.mkdir(path, mode=0o700)
        else:
            statinfo = os.stat(path)
            if not os.path.isdir(path) or os.path.islink(path):
                print("Error: invalid database path {} (it must be a directory)".format(path))
                exit(2)
            elif stat.filemode(statinfo.st_mode) != 'drwx------' :
                print("Error: invalid database path {} (it must have only read, write and excecution permissions for user)".format(path))
                exit(2)
            elif statinfo.st_uid != os.getuid() :
                print("Error: invalid database path {} (the owner must be the user)".format(path))
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
                print("Error: invalid configuration file {} (it must be a regular file)".format(path))
                exit(2)
            elif stat.filemode(statinfo.st_mode) != '-rw-------' :
                print("Error: invalid configuration file {} (it must have only read and write permissions for user)".format(path))
                exit(2)
            elif statinfo.st_uid != os.getuid() :
                print("Error: invalid configuration file {} (the owner must be the user)".format(path))
                exit(2)
        return True
            
    @staticmethod
    def __load_config_file__(fileparser):
        """Load configuration file"""
        try:
            fileparser.read(Configuration.configfile)
        except:
            print("Error: parsing error of configuration file {}".format(Configuration.configfile))
            exit(2)
        else:
            Configuration.port = int(fileparser['DEFAULT']['port'])
            Configuration.dbpath = fileparser['DEFAULT']['dbpath']
            Configuration.poolsize = int(fileparser['DEFAULT']['poolsize'])
    
    @staticmethod
    def __create_config_file__(fileparser):
        """Method to create default configuration file"""
        fileparser['DEFAULT'] = {'port': str(Configuration.port), \
                                 'dbpath': Configuration.dbpath, \
                                 'poolsize': str(Configuration.poolsize)}
        with open(Configuration.configfile, 'w') as configfile:
            fileparser.write(configfile)
        os.chmod(Configuration.configfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IREAD | stat.S_IWRITE)
    
    @staticmethod
    def configure():
        """Configure the server: load configuration file then parse command line"""
        
        # Create, configure a configuration file parser and parse
        fileparser = configparser.ConfigParser()
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
                               have read, write and execution permissions.", \
                               action=MyParserAction)
        # Pool executor size
        argparser.add_argument('-s', '--poolsize', type=int, default=Configuration.poolsize, \
                               metavar='pool_size', help="the size of the pool of execution", \
                               action=MyParserAction)
        # Program version
        argparser.add_argument('-v', '--version', action='version', version='version ' + Configuration.version)
        
        argparser.parse_args() # Parse the command line
        
        # Verify dbpath
        Configuration.__test_dbpath__(Configuration.dbpath)
        
if __name__ == '__main__':
    Configuration.configure()
    print(Configuration.dbpath)
    print(Configuration.port)
    print(Configuration.poolsize)

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

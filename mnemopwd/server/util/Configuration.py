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
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(MyParserAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-s', '--poolsize'] :
            Configuration.poolsize = values
        if option_string in ['-d', '--dbpath']:
            Configuration.dbpath = values
        if option_string in ['-p', '--port'] :
            if values in range(49152,65535):
                Configuration.port = int(values)
            else:
                parser.error("argument -p/--port: invalid choice: {} (choose between 49152 and 65535)".format(values))

class Configuration:
    """Configuration of the server"""
    
    configfile = os.path.expanduser('~') + '/.mnemopwd' # Configuration file
    dbpath = os.path.expanduser('~') + '/data/' # Default database path
    version = '0.1'     # Server version
    host = '127.0.0.1'  # Default host
    port = 62230        # Default port
    poolsize = 10       # Default pool executor size
    
    @staticmethod
    def __treat_config_file__(fileparser):
        fileparser.read(Configuration.configfile)
        Configuration.port = int(fileparser['DEFAULT']['port'])
        Configuration.dbpath = fileparser['DEFAULT']['dbpath']
        Configuration.poolsize = int(fileparser['DEFAULT']['poolsize'])
    
    @staticmethod
    def __create_config_file__(fileparser):
        fileparser['DEFAULT'] = {'port': str(Configuration.port), \
                                 'dbpath': Configuration.dbpath, \
                                 'poolsize': str(Configuration.poolsize)}
        with open(Configuration.configfile, 'w') as configfile:
            fileparser.write(configfile)
        os.chmod(Configuration.configfile, stat.S_IRUSR | stat.S_IWUSR)
    
    @staticmethod
    def configure():
        """Configure the server: load configuration file then parse command line"""
        
        # Create, configure a configuration file parser and parse
        fileparser = configparser.ConfigParser()
        if os.path.exists(Configuration.configfile) :
            # Load values from configuration file
            Configuration.__treat_config_file__(fileparser)
        else:
            # Create default configuration file
            Configuration.__create_config_file__(fileparser)
        
        # Create, configure a command line parser and parse the command line
        argparser = argparse.ArgumentParser(description='MnemoPwd server v' + Configuration.version, \
                                            epilog='More informations can be found at https://github.com/thethythy/Mnemopwd', \
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        argparser.add_argument('-p', '--port' , type=int, nargs='?', default=Configuration.port, \
                               metavar='port', help='the server connexion port', \
                               action=MyParserAction)
        argparser.add_argument('-d', '--dbpath', nargs='?', default='HOME_DIRECTORY/data', \
                               metavar='path', type=str, help="the directory to store \
                               secret data; it will be created if it does not exist; \
                               if the directory already exists only the user must \
                               have read and write permissions.", action=MyParserAction)
        argparser.add_argument('-s', '--poolsize', type=int, default=Configuration.poolsize, \
                               metavar='pool_size', help="the size of the pool of execution", \
                               action=MyParserAction)
        argparser.add_argument('-v', '--version', action='version', version='version ' + Configuration.version)
        argparser.parse_args()
        
if __name__ == '__main__':
    Configuration.configure()
    print(Configuration.dbpath)
    print(Configuration.port)
    print(Configuration.poolsize)

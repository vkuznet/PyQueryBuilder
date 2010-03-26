#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
Config utilities
"""

__revision__ = "$Id: das_config.py,v 1.33 2010/03/10 01:19:56 valya Exp $"
__version__ = "$Revision: 1.33 $"
__author__ = "Valentin Kuznetsov"

import os
import ConfigParser

def configfile():
    """
    Return configuration file name $QB_ROOT/etc/main.cfg
    """
    if  os.environ.has_key('QB_ROOT'):
        config_file = os.path.join(os.environ['QB_ROOT'], 'etc/main.cfg')
        return config_file
    else:
        raise EnvironmentError('QB_ROOT environment is not set up')

def readconfig():
    """
    Read configuration file and store DAS parameters into returning
    dictionary.
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile())
    configdict = {}

    configdict['server_port'] = config.get('server', 'server_port', 8212)
    configdict['verbose'] = config.getint('server', 'verbose')
    return configdict

def writeconfig():
    """
    Write configuration file
    """
    config = ConfigParser.ConfigParser()
    config.add_section('server')
    config.set('server', 'verbose', 0)
    config.set('server', 'logdir', '/tmp')
    config.set('server', 'server_port', 8310)
    config.write(open(configfile(), 'wb'))

if  __name__ == '__main__':
    writeconfig()

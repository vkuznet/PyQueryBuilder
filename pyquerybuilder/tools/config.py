#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
Config utilities
get idea from DAS by Valentin
"""

__revision__ = "$Id: pyqb_config $"
__version__ = "$Revision: $"
__author__ = "Dong"

import os
import ConfigParser

def configfile():
    """
    Return configuration file name $QB_ROOT/etc/main.cfg
    """
    if  os.environ.has_key('QB_ROOT'):
        config_file = os.path.join(os.environ['QB_ROOT'], 'etc/main.cfg')
        if os.path.isfile(config_file):
            return config_file
        else:
            raise EnvironmentError('Configuration file %s not found' % \
                config_file)
    else:
        raise EnvironmentError('QB_ROOT environment is not set up')

def readconfig():
    """
    Read configuration file and store parameters into returning
    dictionary.
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile())
    configdict = {}

    configdict['server_port'] = config.get('server', 'server_port', 8212)
    configdict['verbose'] = config.getint('server', 'verbose')
    db_url = config.get('server', 'db_url')
    if db_url == 'tests/test.db':
        configdict['db_url'] = 'sqlite:///%s/tests/test.db' % \
                                 os.environ['QB_ROOT']
    else:
        configdict['db_url'] = db_url
#    configdict['db_alias'] = config.get('server', 'db_alias')
    configdict['map_file'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'map_file', ''))
    configdict['alias_mapfile'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'alias_mapfile', ''))
    configdict['split_file'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'split_file', ''))
    configdict['logconfig'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'logconfig', ''))
    configdict['doc_dir'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'doc_dir', ''))
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
    config.set('server', 'map_file', 'map.yaml')
    config.set('server', 'alias_mapfile', 'map2.yaml')
    config.set('server', 'split_file', 'split.yaml')
    config.set('server', 'logconfig', 'logconfig')
    config.write(open(configfile(), 'wb'))

if  __name__ == '__main__':
#    writeconfig()
    print readconfig()

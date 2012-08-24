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
    configdict['left_join'] = os.path.join(os.environ['QB_ROOT'], \
                            config.get('server', 'left_join', ''))

    configdict['environment'] = config.get('server', 'environment', 'production')
    configdict['profiler'] = int(config.get('server', 'profiler', 0))
    configdict['threadpool'] = int(config.get('server', 'thread_pool', 30))
    configdict['socket_queue_size'] = int(config.get('server', 'socket_queue_size', 15))
    configdict['expires'] = int(config.get('server', 'expires', 300))
    configdict['log_screen'] = bool(config.get('server', 'log_screen', True))
    configdict['access_log_file'] = config.get('server', 'access_log_file', \
    '/tmp/access_log.log')
    configdict['error_log_file'] = config.get('server', 'error_log_file', \
    '/tmp/error_log.log')
    configdict['access_log_level'] = int(config.get('server', 'access_log_level', 0))
    configdict['error_log_level'] = int(config.get('server', 'error_log_level', 0))
    configdict['algo'] = config.get('server', 'algo', 'MIS')

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
    config.set('server', 'left_join', 'left.yaml')
    config.set('server', 'logconfig', 'logconfig')
    config.write(open(configfile(), 'wb'))

if  __name__ == '__main__':
#    writeconfig()
    print readconfig()

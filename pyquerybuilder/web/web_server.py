#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
#pylint: disable-msg=W0702,E1101
"""
Data server based on CherryPy web framework. We define Root class and
pass it into CherryPy web server.
"""

__revision__ = "$Id: $"
__version__ = "$Revision: 1.6 $"
__author__ = "Valentin Kuznetsov"

# system modules
#import os
#import sys
import yaml
import logging
from optparse import OptionParser

# CherryPy modules
from cherrypy import log, tree, engine
from cherrypy import config as cpconfig
import cherrypy

# local modules

#create logger
logger = logging.getLogger("ConstructQuery")
logger.setLevel(logging.DEBUG)
#create console handler and set level to debug
fh = logging.FileHandler('/tmp/pyqb.log')
fh.setLevel(logging.DEBUG)
#create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#add formatter to fh
fh.setFormatter(formatter)
#add fh to logger
logger.addHandler(fh)


from pyquerybuilder.tools.config import readconfig
from pyquerybuilder.web.web_manager import WebServerManager
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.qb.pyqb import QueryBuilder
from pyquerybuilder.dbsh.dbresults import Results


from cherrypy.process import plugins

class QueryBuilderBus(plugins.SimplePlugin):
    """
    A WSPBus plugin that controls
      1. a SQLAlchemy engine/connection pool.
      2. a QueryBuilder
    """
    def __init__(self, bus, url=None, map_file=None):
        plugins.SimplePlugin.__init__(self, bus)
        self.url = url
        self.dbm = DBManager()
        self.qbs = QueryBuilder()
        self.qbs.set_mapper(map_file)
        self.db_result = Results()
        self.con = None

    def start(self):
        """get db connection"""
        print 'Connecting to database '
        self.con = self.dbm.connect(self.url)
        self.qbs.set_from_tables(self.dbm.load_tables( \
                 self.dbm.get_alias(self.url)))
        if self.dbm.db_type[self.dbm.get_alias(self.url)] == 'mysql':
            self.qbs.mapper.set_sens(True)
        self.qbs.recognize_schema(self.dbm, \
                self.dbm.get_alias(self.url))

    def stop(self):
        """close db connection"""
        self.con.close()
        self.con = None


class Root(object):
    """
    Web server class.
    """
    def __init__(self, config):
        self.config = config
        self.app    = "Root"

    def configure(self):
        """Configure server, CherryPy and the rest."""
        try:
            cpconfig.update ({"server.environment": self.config['environment']})
        except:
            cpconfig.update ({"server.environment": 'production'})
        try:
            cpconfig.update ({"server.thread_pool": self.config['thread_pool']})
        except:
            cpconfig.update ({"server.thread_pool": 30})
        try:
            cpconfig.update ({"server.socket_queue_size": \
                             self.config['socket_queue_size']})
        except:
            cpconfig.update ({"server.socket_queue_size": 15})
        try:
            cpconfig.update ({"server.socket_port": int(self.config['port'])})
        except:
            cpconfig.update ({"server.socket_port": 8080})
        try:
            cpconfig.update ({"server.socket_host": self.config['host']})
        except:
            cpconfig.update ({"server.socket_host": '0.0.0.0'})
        try:
            cpconfig.update ({'tools.expires.secs':
                                int(self.config['expires'])})
        except:
            cpconfig.update ({'tools.expires.secs': 300})
        try:
            cpconfig.update ({'tools.staticdir.on': True})
            cpconfig.update ({'tools.staticdir.dir': self.config['doc_dir']})
        except:
            cpconfig.update ({'tools.staticdir.on': False})
        try:
            cpconfig.update ({'log.screen':
                                bool(self.config['log_screen'])})
        except:
            cpconfig.update ({'log.screen': True})
        try:
            cpconfig.update ({'log.access_file':
                                self.config['access_log_file']})
        except:
            cpconfig.update ({'log.access_file': None})
        try:
            cpconfig.update ({'log.error_file':
                                self.config['error_log_file']})
        except:
            cpconfig.update ({'log.error_file': None})
        try:
            log.error_log.setLevel(self.config['error_log_level'])
        except:
            log.error_log.setLevel(logging.DEBUG)
        try:
            log.access_log.setLevel(self.config['access_log_level'])
        except:
            log.access_log.setLevel(logging.DEBUG)
        cpconfig.update ({
                          'tools.expires.on': True,
                          'tools.response_headers.on':True,
                          'tools.etags.on':True,
                          'tools.etags.autotags':True,
                          'tools.encode.on': True,
                          'tools.gzip.on': True
                          })
        #cpconfig.update ({'request.show_tracebacks': False})
        #cpconfig.update ({'request.error_response': self.handle_error})
        #cpconfig.update ({'tools.proxy.on': True})
        #cpconfig.update ({'proxy.tool.base': '%s:%s' 
#                                % (socket.gethostname(), opts.port)})

        log("loading config: %s" % cpconfig,
                                   context=self.app,
                                   severity=logging.DEBUG,
                                   traceback=False)

    def start(self, blocking=True):
        """Configure and start the server."""
        self.configure()
        config = {'db_url':self.config['db_url'],
                  'map_file':self.config['map_file']}
        # can be something to consider
        obj = WebServerManager(config) # mount the web server manager
        if self.config.get('profiler', 0):
            from pyquerybuilder.web.profiler import cachegrind
            cherrypy.tools.cachegrind = cherrypy.Tool('before_handler', \
                    cachegrind, priority=100)
            toolconfig = {'/' : {'tools.cachegrind.on' : True}, }
            tree.mount(obj, '/', toolconfig)
        else:
            tree.mount(obj, '/')

        # mount static document directory
        dirs = self.config['doc_dir'].split('/html')
        doc_config = {'/':
                       { 'tools.staticdir.root': dirs[0],
                         'tools.staticdir.dir': 'html',
                         'tools.staticdir.on': True,}}
        tree.mount(None, '/doc', doc_config)

        engine.start()
        if  blocking:
            engine.block()

    def stop(self):
        """Stop the server."""
        engine.exit()
        engine.stop()

def main():
    """
    Start-up web server.
    """
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config", default=False,
        help="provide cherrypy configuration file")
    opts, _ = parser.parse_args()

    # Read server configuration
    conf_file = opts.config
    config = {}
    if  conf_file:
        fdesc  = open(conf_file, 'r')
        config = yaml.load(fdesc.read())
        fdesc.close()
    else:
        config = readconfig()
    config['port'] = config['server_port']

    root = Root(config)
    print root.config
    # subscribe plugins
    cherrypy.engine.qbm = QueryBuilderBus(cherrypy.engine, \
                           root.config['db_url'], root.config['map_file'])

    cherrypy.engine.qbm.subscribe()


    # Start PyQB server
    root.start()


if __name__ == "__main__":
    main()

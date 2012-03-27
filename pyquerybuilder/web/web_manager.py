#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
Web server.
"""

__revision__ = "$Id: $"
__version__ = "$Revision: 1.3 $"
__author__ = "Valentin Kuznetsov"
__email__ = "vkuznet@gmail.com"

# system modules
import os
import sys
import time
import urllib

# cherrypy modules
import cherrypy
from cherrypy import expose, response, tools
from cherrypy.lib.static import serve_file
from cherrypy import config as cherryconf

from pyquerybuilder.web.tools import exposecss, exposejs, exposejson
from pyquerybuilder.web.tools import TemplatedPage

#from pyquerybuilder.qb.pyqb import QueryBuilder
from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.dbsh.dbresults import Results
#from pyquerybuilder.db.DBManager import DBManager
import traceback

def set_headers(itype, size=0):
    """
    Set response header Content-type (itype) and Content-Length (size).
    """
    if  size > 0:
        response.headers['Content-Length'] = size
    response.headers['Content-Type'] = itype
    response.headers['Expires'] = 'Sat, 14 Oct 2017 00:59:30 GMT'

def minify(content):
    """
    Remove whitespace in provided content.
    """
    content = content.replace('\n', ' ')
    content = content.replace('\t', ' ')
    content = content.replace('   ', ' ')
    content = content.replace('  ', ' ')
    return content

class WebManager(TemplatedPage):
    """
    Web manager.
    """
    def __init__(self, config):
        TemplatedPage.__init__(self, config)
        self.base = '' # defines base path for HREF in templates
        imgdir = '%s/%s' % (__file__.rsplit('/', 1)[0], 'images')
        cssdir = '%s/%s' % (__file__.rsplit('/', 1)[0], 'css')
        jsdir  = '%s/%s' % (__file__.rsplit('/', 1)[0], 'js')
        docdir = '%s/%s' % (__file__.rsplit('/', 2)[0], 'doc')
        print "IMG dir", imgdir
        print "CSS dir", cssdir
        print "JS  dir", jsdir
        print "Document dir", docdir
        self.cssmap   = {
            'main.css': cssdir + '/main.css',
        }
        self.jsmap    = {
            'utils.js': jsdir + '/utils.js',
            'ajax_utils.js': jsdir + '/ajax_utils.js',
            'prototype.js': jsdir + '/prototype.js',
        }
        self.imagemap = {
            'loading.gif': imgdir + '/loading.gif',
            'QB_logo.png': imgdir + '/QB_logo.png',
        }
        self.cache    = {}

    @expose
    def index(self, *args, **kwargs):
        """Main page"""
        page = "Web Server"
        return self.page(page)

    def top(self):
        """
        Provide masthead for all web pages
        """
        return self.templatepage('cmssw_top', base=self.base)

    def bottom(self):
        """
        Provide footer for all web pages
        """
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        ctime = 0
        return self.templatepage('cmssw_bottom', div="", services="",
                timestamp=timestamp, ctime=ctime)

    def page(self, content):
        """
        Provide page wrapped with top/bottom templates.
        """
        page  = self.top()
        page += content
        page += self.bottom()
        return page

    @expose
    def images(self, *args, **kwargs):
        """
        Serve static images.
        """
        mime_types = ['*/*', 'image/gif', 'image/png',
                      'image/jpg', 'image/jpeg']
        accepts = cherrypy.request.headers.elements('Accept')
        for accept in accepts:
            if  accept.value in mime_types and len(args) == 1 \
                and self.imagemap.has_key(args[0]):
                image = self.imagemap[args[0]]
                # use image extension to pass correct content type
                ctype = 'image/%s' % image.split('.')[-1]
                cherrypy.response.headers['Content-type'] = ctype
                return serve_file(image, content_type=ctype)

    @exposecss
    @tools.gzip()
    def css(self, *args, **kwargs):
        """
        Cat together the specified css files and return a single css include.
        Get css by calling: /controllers/css/file1/file2/file3
        """
        mime_types = ['text/css']
        cherryconf.update({'tools.encode.on': True,
                           'tools.gzip.on': True,
                           'tools.gzip.mime_types': mime_types,
                          })

        args = list(args)
        scripts = self.check_scripts(args, self.cssmap)
        idx = "-".join(scripts)

        if  idx not in self.cache.keys():
            data = '@CHARSET "UTF-8";'
            for script in args:
                if  self.cssmap.has_key(script):
                    path = os.path.join(sys.path[0], self.cssmap[script])
                    path = os.path.normpath(path)
                    ifile = open(path)
                    data = "\n".join ([data, ifile.read().\
                        replace('@CHARSET "UTF-8";', '')])
                    ifile.close()
            set_headers ("text/css")
            self.cache[idx] = minify(data)
        return self.cache[idx]

    @exposejs
    @tools.gzip()
    def js(self, *args, **kwargs):
        """
        Cat together the specified js files and return a single js include.
        Get js by calling: /controllers/js/file1/file2/file3
        """
        mime_types = ['application/javascript', 'text/javascript',
                      'application/x-javascript', 'text/x-javascript']
        cherryconf.update({'tools.gzip.on': True,
                           'tools.gzip.mime_types': mime_types,
                           'tools.encode.on': True,
                          })

        args = list(args)
        scripts = self.check_scripts(args, self.jsmap)
        idx = "-".join(scripts)

        if  idx not in self.cache.keys():
            data = ''
            for script in args:
                path = os.path.join(sys.path[0], self.jsmap[script])
                path = os.path.normpath(path)
                ifile = open(path)
                data = "\n".join ([data, ifile.read()])
                ifile.close()
            self.cache[idx] = data
        return self.cache[idx]

    def check_scripts(self, scripts, map):
        """
        Check a script is known to the map and that the script actually exists
        """
        for script in scripts:
            if script not in map.keys():
                self.warning("%s not known" % script)
                scripts.remove(script)
            else:
                path = os.path.join(sys.path[0], map[script])
                path = os.path.normpath(path)
                if not os.path.exists(path):
                    self.warning("%s not found at %s" % (script, path))
                    scripts.remove(script)
        return scripts

class WebServerManager(WebManager):
    """
    WebServerManager interface.
    """
    def __init__(self, config):
        WebManager.__init__(self, config)
        self.base = '' # define base url path, no path is required right now
#        self.dbm = DBManager()
#        self.pyqb = QueryBuilder()
#        try:
#            self.pyqb.set_mapper(config['map_file'])
#            self.dbm.connect(config['db_url'])
#            db_alias = self.dbm.get_alias(config['db_url'])
#            tables = self.dbm.load_tables(db_alias)
#            self.pyqb.set_from_tables(tables)
#        except Error:
#            traceback.print_exc()
#        self.db_result = Results()
        self.c_titles = []

    @expose
    def index(self, *args, **kwargs):
        """Serve default index.html web page"""
        return self.page()

    @expose
    def cli(self, *args, **kwargs):
        """
        Serve CLI file download.
        """
        clifile = os.path.join(os.environ['QB_ROOT'],
                'pyquerybuilder/tools/qbcli.py')
        return serve_file(clifile, content_type='text/plain')

    @expose
    def faq(self, *args, **kwargs):
        """
        Serve FAQ pages
        """
        page = self.templatepage('faq')
        return self.page(page)

    @expose
    def bugs(self, *args, **kwargs):
        """
        Serve bugs page
        """
        page = self.templatepage('bugs')
        return self.page(page)

    def top(self):
        """
        Define masthead for all web pages
        """
        return self.templatepage('top', base=self.base)

    def bottom(self):
        """
        Define footer for all web pages
        """
        return self.templatepage('bottom')

    def page(self, content='', ctime=None):
        """
        Define footer for all web pages
        """
        page  = self.top()
        page += self.templatepage('search', base=self.base)
        page += content
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        page += self.templatepage('bottom', ctime=ctime, timestamp=timestamp)
        return page

    def get_data(self, uinput, idx, limit, sort, sdir):
        """
        Retrieves data from the back-end
        """
        keywords = [ keys.strip().replace('(', '').replace(')', \
                    '').replace('.', '') for keys in \
                    uinput.split('where')[0].split('find')[1].split(',')]
        query = cherrypy.engine.qbm.dbm.explain_query(uinput)
        result = cherrypy.engine.qbm.dbm.execute_with_slice(\
                    query, limit, idx, keywords.index(sort), sdir)

        t_list = keywords
        o_list = result[1]
        rows = []
        if o_list == {}:
            record = {}
            for title in t_list:
                record[title] = ''
            rows.append(record)
        for res in o_list:
            index = 0
            record = {}
            for index in range(0, len(t_list)):
                record[t_list[index]] = str(res[index])
            rows.append(record)
#        if sdir == 'asc':
#            rows.sort()
#        elif  sdir == 'desc':
#            rows.sort()
#            rows.reverse()
#        print rows
        return rows

    def get_total(self, uinput):
        """Gets total number of results for provided input, i.e. count(*)"""
        return cherrypy.engine.qbm.dbm.get_total(uinput)

    @exposejson
    def yuijson(self, **kwargs):
        """
        Provides JSON in YUI compatible format to be used in DynamicData table
        widget, see
        http://developer.yahoo.com/yui/examples/datatable/dt_dynamicdata.html
        """
#        print "\n###call yuijson", kwargs
        sort   = kwargs.get('sort', 'id')
        uinput = kwargs.get('input', '')
        limit  = int(kwargs.get('limit', 50)) # number of shown results
        idx    = int(kwargs.get('idx', 0)) # start with
        sdir   = kwargs.get('dir', 'asc')
        rows   = self.get_data(uinput, idx, limit, sort, sdir)
#        rows   = self.get_data(uinput, limit, idx)
        total  = self.get_total(uinput)
        jsondict = {'recordsReturned': len(rows),
                   'totalRecords': total,
                   'startIndex':idx,
                   'sort':'false',
                   'dir':'asc',
                   'pageSize': limit,
                   'records': rows}
#        print "\n###jsondict", jsondict
        return jsondict

    @expose
    def results(self, *args, **kwargs):
        """
        Page representing result table
        """
#        print "\n### call results", args, kwargs
        uinput = kwargs.get('input', '')
        if  not uinput:
            return self.error
        manager = cherrypy.engine.qbm
        keywords = []
        try:
            if cherrypy.engine.qbm.qbs == None:
                raise Exception, "qbs is None"
                self.log("qbs is None", 1)
        except Error:
            traceback.print_exc()
        limit = 50
        try:
            mquery = manager.dbm.explain_query(uinput)
            if mquery == None:
                mquery = manager.qbs.build_query(uinput)
                manager.dbm.set_query_explain(uinput, mquery)
                manager.dbm.set_total(uinput, mquery)
        except Error:
            traceback.print_exc()
        keywords = [ keys.strip().replace(')', '').replace('(', \
                    '').replace('.', '') for keys in \
                    uinput.split('where')[0].split('find')[1].split(',')]
        titles = keywords
        cherrypy.engine.qbm.dbm.page('%d' % limit)
        coldefs = ""
        myfields = ""
        for t_index in range(0, len(titles)):
            coldefs += "{key:'%s',label:'%s',sortable:true,resizeable:true}," \
                        % (titles[t_index], keywords[t_index])
            myfields += "{key:'%s'}," % titles[t_index]

        coldefs = "[%s]" % coldefs[:-1] # remove last comma
        myfields = "[%s]" % myfields[:-1]
        coldefs = coldefs.replace("},{", "},\n{")
        myfields = myfields.replace("},{", "},\n{")

        total   = self.get_total(uinput)

        names   = {'title1':titles[0],
                   'coldefs':coldefs,
                   'rowsperpage':limit,
                   'total':total,
                   'tag':'mytag',
                   'input':urllib.quote(uinput),
                   'fields':myfields}
        page    = self.templatepage('table', **names)
        page    = self.page(page)
        return page

    @expose
    def error(self, msg=''):
        """Return error page"""
        return self.page(msg)


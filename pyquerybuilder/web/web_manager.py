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
import json
#import types
from itertools import izip
# cherrypy modules
import cherrypy
from cherrypy import expose, response, tools
from cherrypy.lib.static import serve_file
from cherrypy import config as cherryconf

from pyquerybuilder.web.tools import exposecss, exposejs, exposejson
from pyquerybuilder.web.tools import TemplatedPage
from pyquerybuilder.web.tools import formatpath

#from pyquerybuilder.qb.pyqb import QueryBuilder
from pyquerybuilder.utils.Errors import Error
#from pyquerybuilder.dbsh.dbresults import Results
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
#        docdir = '%s/%s' % (__file__.rsplit('/', 2)[0], 'doc')
        print "IMG dir", imgdir
        print "CSS dir", cssdir
        print "JS  dir", jsdir
#        print "Document dir", docdir
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

    def check_scripts(self, scripts, maps):
        """
        Check a script is known to the map and that the script actually exists
        """
        for script in scripts:
            if script not in maps.keys():
                self.warning("%s not known" % script)
                scripts.remove(script)
            else:
                path = os.path.join(sys.path[0], maps[script])
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
        self.total_cache = {}

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
        page  = self.top()
        page += self.templatepage('faq')
        mapper = cherrypy.engine.qbm.qbs.get_mapper()
        attr_path = cherrypy.engine.qbm.qbs.get_attr_path()
        keys = mapper.list_key()
        variables = {'entities':{},
                     'prim':{},
                     'path':{},}
        entities = variables['entities']
        prim = variables['prim']
        path = variables['path']
        for key in keys:
            names = key.split('.')
            if len(names) == 1:
                if not entities.has_key(key):
                    entities[key] = {}
                    prim[key] = mapper.get_column(key)
            else:
                if not entities.has_key(names[0]):
                    entities[names[0]] = {}
                    prim[names[0]] = mapper.get_key(mapper.get_column(key))
                entities[names[0]][names[1]] = mapper.get_column(key).lower()
                if attr_path.has_key(key):
                    if not path.has_key(names[0]):
                        path[names[0]] = {}
                    path[names[0]][names[1]] = formatpath(attr_path[key])
        page += self.templatepage('ktable', **variables)
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        page += self.templatepage('bottom', ctime=None, timestamp=timestamp)
        return page

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
        and total number of results for provided input, i.e. count(*)
        """
        keywords = [ keys.strip().replace('(', '').replace(')', \
                    '').replace('.', '') for keys in \
                    uinput.split('where')[0].split('find')[1].split(',')]
        query = cherrypy.engine.qbm.dbm.explain_query(uinput)
        t_cursor, cursor = cherrypy.engine.qbm.dbm.execute_with_slice(\
                    query, limit, idx, keywords.index(sort), sdir)

        total = t_cursor.fetchone()
        if total:
            total = total[0]
        else:
            total = 0
        t_list = keywords
        results = []
        rapp = results.append
        while True:
            if not cursor.closed:
                rows = cursor.fetchmany(size=50)
                if not rows:
                    cursor.close()
                    break
                for rec in rows:
                    rapp(dict(izip(t_list, rec)))
            else:
                break
        if not cursor.closed:
            cursor.close()
        return total, results

    def get_total(self, mquery):
        """Gets total number of results for provided input, i.e. count(*)"""
        return cherrypy.engine.qbm.dbm.get_total(mquery)

    def get_cached_total(self, mquery):
        """Gets totalnumber of results"""
        qid = hash(str(mquery))
        if not self.total_cache.has_key(qid):
            total = cherrypy.engine.qbm.dbm.get_total(mquery)
            self.total_cache[qid] = total
        return self.total_cache[qid]


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
        total, rows   = self.get_data(uinput, idx, limit, sort, sdir)
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
        except Error:
            traceback.print_exc()
        limit = 50
        try:
            mquery = manager.dbm.explain_query(uinput)
            if mquery == None:
                mquery = manager.qbs.build_query(uinput)
                if mquery == None:
                    self.log('invalid query', 2)
                    return self.page("invalid query")
                manager.dbm.set_query_explain(uinput, mquery)
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

        total   = self.get_total(mquery)

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
    def jsonresults(self, *args, **kwargs):
        """return json results"""
        cherrypy.response.headers["Content-Type"] = "application/json"
        uinput = kwargs.get('input', '')
        if  not uinput:
            return json.dumps({'error':"empty input"})
        manager = cherrypy.engine.qbm
        mquery = None
        try:
            mquery = manager.dbm.explain_query(uinput)
            if mquery == None:
                mquery = manager.qbs.build_query(uinput)
                if mquery == None:
                    self.log('invalid query', 2)
                    return json.dumps({'error':"invalid query"})
                manager.dbm.set_query_explain(uinput, mquery)
        except Error:
            traceback.print_exc()

        total = self.get_cached_total(mquery)
        if total > 3000:
            qline = kwargs['input']
            streamapi = "/stream?input=" + qline
            raise cherrypy.InternalRedirect(streamapi)
        return self.get_json_data(uinput, mquery)

    @expose
    def stream(self, *args, **kwargs):
        """
        stream json output
        http://www.enricozini.org/2011/tips/python-stream-json/
        """
        cherrypy.response.headers["Content-Type"] = "application/json"
        uinput = kwargs.get('input', '')
        if not uinput:
            return json.dumps({'error':"empty input"})
        manager = cherrypy.engine.qbm
        mquery = None
        try:
            mquery = manager.dbm.explain_query(uinput)
        except Error:
            traceback.print_exc()
        if mquery == None:
            mquery = manager.qbs.build_query(uinput)
        if mquery == None:
            self.log('invalid query', 2)
            return json.dumps({'error':"invalid query"})

        t_list = [ keys.strip() for keys in \
                    uinput.split('where')[0].split('find')[1].split(',') ]
        cursor = cherrypy.engine.qbm.dbm.execute(mquery)
        chunk_size = 3000
        return pack_stream(cursor, t_list, chunk_size)

    stream._cp_config = {'response.stream': True}

    def get_json_data(self, uninput, query):
        """
        Retrieves data from the back-end
        """
        t_list = [ keys.strip() for keys in \
                    uninput.split('where')[0].split('find')[1].split(',') ]
        cursor = cherrypy.engine.qbm.dbm.execute(query)
        return pack_result(cursor, t_list)

    @expose
    def error(self, msg=''):
        """Return error page"""
        return self.page(msg)

    #@cherrypy.tools.redirect(url='/test', internal=True)
    def testred(self, *args, **kwargs):
        query = kwargs['input']
        streamapi = "/stream?input=" + query
        raise cherrypy.InternalRedirect(streamapi)
    testred.exposed = True


def pack_result(cursor, t_list):
    """
    pack result in dictionary and dumps with json
    """
    results = []
    rapp = results.append
    while True:
        if not cursor.closed:
            rows = cursor.fetchmany(size=50)
            if not rows:
                cursor.close()
                break
            for rec in rows:
                rapp(dict(izip(t_list, rec)))
        else:
            break
    if not cursor.closed:
        cursor.close()
    return json.dumps(results)

def pack_stream(cursor, t_list, chunk_size):
    """
    """
    results = []
    rapp = results.append
    output = 0
    while True:
        if not cursor.closed:
            rows = cursor.fetchmany(size=50)
            if not rows:
                cursor.close()
                break
            for rec in rows:
                rapp(dict(izip(t_list, rec)))
            output += 50
            if output >= chunk_size:
                yield json.dumps(results) + '\n'
                results = []
                rapp = results.append
                output = 0
        else:
            break
    if not cursor.closed:
        cursor.close()
    if results != []:
        yield json.dumps(results) + '\n'

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
        print "IMG dir", imgdir
        print "CSS dir", cssdir
        print "JS  dir", jsdir
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
    def __init__(self, config={}):
        WebManager.__init__(self, config)
        self.base = '' # define base url path, no path is required right now

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
        rows    = [{'id':str(r), 'title1':str(r), 'title2':str(r)} \
                        for r in range(0,10)]
        if  sdir == 'desc':
            rows.sort()
            rows.reverse()
        return rows

    def get_total(self, uinput):
        """Gets total number of results for provided input, i.e. count(*)"""
        total = 10
        return total

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
        limit  = int(kwargs.get('limit', 10)) # number of shown results
        idx    = int(kwargs.get('idx', 0)) # start with
        sdir   = kwargs.get('dir', 'desc') 
        rows   = self.get_data(uinput, idx, limit, sort, sdir)
        total  = self.get_total(uinput)
        jsondict = {'recordsReturned': len(rows),
                   'totalRecords': total, 'startIndex':idx,
                   'sort':'true', 'dir':'asc',
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
        titles  = ['id'] + ['title1', 'title2']
        limit   = 10
        coldefs = ""
        for title in titles:
            coldefs += '{key:"%s",label:"%s",sortable:true,resizeable:true},' \
                        % (title, title)
        coldefs = "[%s]" % coldefs[:-1] # remove last comma
        coldefs = coldefs.replace("},{","},\n{")

        uinput  = kwargs.get('input', '')
        if  not uinput:
            return self.error

        total   = self.get_total(uinput)
        names   = {'titlelist':titles,
                   'coldefs':coldefs, 'rowsperpage':limit,
                   'total':total, 'tag':'mytag',
                   'input':urllib.quote(uinput)}
        page    = self.templatepage('table', **names)
        page    = self.page(page)
        return page

    @expose
    def error(self, msg=''):
        """Return error page"""
        return self.page(msg)


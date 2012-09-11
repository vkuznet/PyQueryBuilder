#!/usr/bin/env python
"""
Very simple client:
"""
import sys
import os
#import cjson
import json
import getopt
import time
import urllib, urllib2


class PyQBClient:
    def __init__(self, baseurl):
        self.baseurl = baseurl
        self.header =  {"Accept": "application/json"}
        self.opener =  urllib2.build_opener()

    def get(self, params):
        "method for GET verb"
        url = self.baseurl
        if not params == {}:
            url = "?".join((url, urllib.urlencode(params, doseq=True)))
#            url = url+'&chunk_size=2'
        #req = urllib2.Request(url = url, headers = self.header)
        req = urllib2.Request(url = url)
        data = self.opener.open(req)
        result = []
        if data.headers.has_key('content-length'):
        #ddata = cjson.decode(data.read())
        #return ddata
            a = data.read()
            data.close()
            result = json.loads(a)
        else:
            a = data.readline()
            while a:
                result.extend(json.loads(a))
                a = data.readline()
            data.close()
        return result

    def put(self, indata):
        """method for PUT verb"""
        url = self.baseurl
        header = self.header
        header['Content-Type'] = 'application/json'
        endata = cjson.encode(indata)
        req = urllib2.Request(url = url, data = endata, headers = header)
        req.get_method = lambda: 'POST'
        self.opener.open(req)

def usage():
    progName = os.path.basename(sys.argv[0])
    print "Usage:"
    print "  %s -q=<query> -f=<query_file>" % progName
    print "     -u=<url> -m=<mapfile>"
    print " "

if __name__ == "__main__":
    query = None
    qfile = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "q:f:", \
            ["query=", "file=",])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, oarg in opts:
        if opt in ("-q", "--query"):
            query = oarg
        elif opt in ("-f", "--file"):
            qfile = oarg

    if opts == []:
        usage()
        sys.exit(2)

    URLBASE = "http://cmsweb.ihep.ac.cn:8310/jsonresults/"
    #URLBASE = "http://vocms09.cern.ch:8989/DBSServlet/"
    CLI = PyQBClient(URLBASE)

    if query or qfile:
        if query:
            st = time.clock()
            res = CLI.get({"input":query})
            print json.dumps(res, sort_keys = True, indent = 4)
            print "total execute time %f" % (time.clock() - st)
            print "total results is %d" % (len(res))
        else:
            count = 0
            ecount = 0
            pcount = 0
            icount = 0
            queries = open(qfile)
            equeries = ""
            empties = ""
            invalids = ""
            st = time.clock()
            for query in queries.readlines():
                print query
                query = query.rstrip()
                try:
                    res = CLI.get({"input":query})
                    if len(res) == 0:
                        empties += query+'\n'
                        pcount += 1
                    if res != [] and res[0].has_key('error'):
                        invalids += query+'\n'
                        icount += 1
                    count += 1
                    print json.dumps(res, sort_keys = True, indent = 4)
                except Exception, e:
                    ecount += 1
                    equeries += query+'\n'

            print "total succeed query is %d" % (count)
            print "total failed query is %d" % (ecount)
            print "total empty query is %d" % (pcount)
            print "total invalid query is %d" % (icount)
            print "total execute time %f" % (time.clock() - st)
#            print "total results is %d" % (len(res))
            print "failed queries is\n", equeries
#            print "empty queries is\n", empties
#            print "invalid queries is\n", invalids

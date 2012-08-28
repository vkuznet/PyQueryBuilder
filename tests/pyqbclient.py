#!/usr/bin/env python
import os
import sys
import traceback
import getopt
import time
from logging import getLogger
from pyquerybuilder.qb.ConfigureLog import configurelog


from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.dbsh.dbprint import PrintOutput
from pyquerybuilder.qb.pyqb import QueryBuilder

#RESULTS = Results()
#SCHEMA_FILE = None
FILE_DICT = {'MAP_FILE':None, 'SCHEMA_FILE':None}

try:
    DB = DBManager()
    DBPRINT = PrintOutput()
    QB = QueryBuilder()
#    FILE_DICT['MAP_FILE'] = os.getenv('HOME')+'/.ipython/map.yaml'
#    QB.set_mapper(FILE_DICT['MAP_FILE'])
except:
    traceback.print_exc()
    raise Exception, DBPRINT.msg_red("ERROR: fail to load DBManager")
try:
    configurelog()
except:
    traceback.print_exc()
    raise Exception, DBPRINT.msg_red("ERROR: fail to configure log")

_LOGGER = getLogger("ConstructQuery")

def connect(arg, alias):
    """
    1. Connect to database via arg, which could be url or dbalias
    2. Set prompt
    3. load schema to QueryBuilder
    """
    DB.connect(arg)
    tables = DB.load_tables(alias)
    QB.set_from_tables(tables)
    if QB.mapper:
        if DB.db_type[alias] == 'mysql':# for mysql case sensitive
            DBPRINT.print_blue('mysql case sensitive')
            QB.mapper.set_sens(True)
        QB.recognize_schema(DB, alias)

def close(alias):
    """
    1. close database connection
    2. set prompt back to dbsh
    """
    DB.close(alias)
    if FILE_DICT['SCHEMA_FILE'] == None :
        return
    if os.path.isfile(FILE_DICT['SCHEMA_FILE']):
        QB.set_from_files(FILE_DICT['SCHEMA_FILE'])
        DBPRINT.print_blue('QB Switch back to Schema file %s' % \
                    FILE_DICT['SCHEMA_FILE'])

def find(arg, alias):
    """Execute QL expressions"""
    query = arg.split(';')[0].strip()
    mquery = QB.build_query(query)
    if mquery == None:
        _LOGGER.debug("failed to build query %s" % query)
        return
    print mquery
    _LOGGER.debug(mquery)
    res = DB.execute(mquery, alias)
    result = DB.print_result(res, mquery)
#    RESULTS.set(result)

def get_total(arg, alias):
    query = arg.split(';')[0].strip()
    mquery = QB.build_query(query)
    if mquery == None:
        _LOGGER.debug("failed to build query %s" % query)
        return
    mquery = mquery._clone()
    if mquery.use_labels:
        mquery = mquery.apply_labels()
        mquery.use_labels = False
    mquery = mquery.count()
    print mquery
    _LOGGER.debug(mquery)
    res = DB.execute(mquery, alias)
    result = DB.print_result(res, mquery)


def mapfile(arg, alias):
    """Set map file for QueryBuilder"""
    if os.path.isfile(arg):
        FILE_DICT['MAP_FILE'] = arg
        QB.set_mapper(FILE_DICT['MAP_FILE'])
        if DB.db_type[alias] == 'mysql':# for mysql case sensitive
            DBPRINT.print_blue('mysql case sensitive')
            QB.mapper.set_sens(True)
        QB.recognize_schema(DB, alias)
        return

def usage():
    progName = os.path.basename(sys.argv[0])
    print "Usage:"
    print "  %s -q=<query> -f=<query_file>" % progName
    print "     -u=<url> -m=<mapfile>"
    print " "

if __name__ == '__main__':
    query = None
    qfile = None
    map_file = None
    url = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "q:f:u:m:", \
            ["query=", "file=", "url=", "mapfile="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, oarg in opts:
        if opt in ("-q", "--query"):
            query = oarg
        elif opt in ("-f", "--file"):
            qfile = oarg
        elif opt in ("-u", "--url"):
            url = oarg
        elif opt in ("-m", "--mapfile"):
            map_file = oarg

    if opts == []:
        usage()
        sys.exit(2)

    if query or qfile and url != None and map_file != None:
        dbalias = DB.dbname(url).split()[0]
        connect(url, dbalias)
        mapfile(map_file, dbalias)
        if query:
            st = time.clock()
            get_total(query, dbalias)
            find(query, dbalias)
            print "total execute time %f" % (time.clock() - st)
        else:
            queries = open(qfile)
            st = time.clock()
            for query in queries.readlines():
                find(query.rstrip(), dbalias)
            print "total execute time %f" % (time.clock() - st)

#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""ipython profile for pyqb sources from db shell"""
# system modules
import os
import sys
#import time
#import types
#import string
#import popen2
import traceback
from logging import getLogger

# ipython modules
from IPython import Release
import IPython.ipapi
IP = IPython.ipapi.get()

from pyquerybuilder.qb.ConfigureLog import configurelog
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.dbsh.dbprint import PrintOutput
from pyquerybuilder.dbsh.dbresults import Results
from pyquerybuilder.dbsh.dbcmd import CMDDICT
from pyquerybuilder.dbsh.dbcmd import CMDDICTEXT
from pyquerybuilder.qb.pyqb import QueryBuilder

#RESULTS = Results()
#SCHEMA_FILE = None
__alias_table__ = {}
FILE_DICT = {'MAP_FILE':None, 'SCHEMA_FILE':None}

try:
    configurelog()
    DB = DBManager()
    DBPRINT = PrintOutput()
    QB = QueryBuilder()
#    FILE_DICT['MAP_FILE'] = os.getenv('HOME')+'/.ipython/map.yaml'
#    QB.set_mapper(FILE_DICT['MAP_FILE'])
except:
    traceback.print_exc()
    raise Exception, DBPRINT.msg_red("ERROR: fail to load DBManager")

_LOGGER = getLogger("ConstructQuery")

def db_ready(supressed=False):
    """Check whether db is connected"""
    if DB.con == None:
        if supressed is True:
            return 0
        DBPRINT.print_red("No DB connection")
        print "To connect to DB, please use command " \
               + DBPRINT.msg_green("connect")
        return 0
    if DB.con.closed:
        if supressed is True:
            return 0
        DBPRINT.print_red("No DB connection")
        print "To connect to DB, please use command " +  \
              DBPRINT.msg_green("connect")
        print "To check saved DB source, please use Command " \
              + DBPRINT.msg_green("mydb")
        return 0
    return 1

def qb_ready():
    """
    Check whether Schema is loaded into QueryBuilder
    1. It can be loaded from DB when DB is connected, after loaded no matter
       DB is connected or closed, QueryBuilder can do translation.
    2. It can be loaded from Schema file.
    Check mapper is ready:
    1. mapfile is loaded
    2. mapper initialized without error
    """
    if not QB.is_ready():
        DBPRINT.print_red("QueryBuilder is not avaliable")
        print "To work with QueryBuilder, schema and map file are both needed."
        if db_ready(supressed=True):
            print "DB is connected\n please check map file with Command %s\n \
for more help check %s" % (DBPRINT.msg_green("mapfile"),
                DBPRINT.msg_green("dbhelp mapfile"))
        else:
            print "No DB conncetion \n checking %s for loading schema from \
DB\n checking %s for loading schema from file\n checking %s for load mapfile" % \
          (DBPRINT.msg_green("connect"), DBPRINT.msg_green("schemafile"), \
                 DBPRINT.msg_green("mapfile"))
        return 1
    return 0

def set_prompt(in1):
    """set prompt as input  """

#    ips = __main__.__dict__['__IP'] 
    ips = IP.user_ns['__IP']
    prompt = getattr(ips.outputcache, 'prompt1')
    prompt.p_template = in1
    prompt.set_p_str()

def get_prompt():
    """get prompt """
#    ips = __main__.__dict__['__IP'] 
    ips = IP.user_ns['__IP']
    prompt = getattr(ips.outputcache, 'prompt1')
    return ips.outputcache.prompt1.p_template

def db_alias():
    """retrieve database alias from prompt """
    prompt = get_prompt()
#    return prompt.split("|")[0].split("-")[1].strip() 
# see how dbshell define dbname and db_alias
#    prom = prompt.split("|")[0].split("-")[1:]
#    alias1 = '-'.join(prom).strip()
    alias1 = prompt.split('|')[0].strip()
#    import pdb
#    pdb.set_trace()
    return alias1 # see how dbshell define dbname and db_alias

def connect(self, arg):
    """
    1. Connect to database via arg, which could be url or dbalias
    2. Set prompt
    3. load schema to QueryBuilder
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'connect')
    DB.connect(arg)
    set_prompt(DB.dbname(arg))
    tables = DB.load_tables(db_alias())
    QB.set_from_tables(tables)
    if QB.mapper:
        if DB.db_type[db_alias()] == 'mysql':# for mysql case sensitive
            DBPRINT.print_blue('mysql case sensitive')
            QB.mapper.set_sens(True)
        QB.recognize_schema(DB, alias)

def close(self, arg):
    """
    1. close database connection
    2. set prompt back to dbsh
    """
    if arg.lower() == 'help':
        return dbhelp(self, 'close')
    if not db_ready():
        return
    DB.close(db_alias())
    set_prompt('dbsh |\#> ')
    if FILE_DICT['SCHEMA_FILE'] == None :
        return
    if os.path.isfile(FILE_DICT['SCHEMA_FILE']):
        QB.set_from_files(FILE_DICT['SCHEMA_FILE'])
        DBPRINT.print_blue('QB Switch back to Schema file %s' % \
                    FILE_DICT['SCHEMA_FILE'])

def rerun(self, arg):
    """re-run last command"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'rerun')
    IP.ex("exec _i%d" % int(arg))

def show(self, arg):
    """
    show command, show arg (;)
         *show tables* will return by our show_table function
         *show x* will be send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'show')
    if not db_ready():
        return
    arg = arg.replace(";","")
    if arg == 'tables':
        DB.show_table(db_alias())
    else:
        DB.execute("show ", db_alias())

def desc(self, arg):
    """desc table"""
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'desc')
    if not db_ready():
        return
    DB.desc(db_alias(), arg.replace(";",""))

def page(self, arg):
    """
    page by inputing offset and limit per page
           *page(offset,limit)*
           *page(limit)*
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'page')
    DB.page(arg)

def next(self, arg = None):
    """
    move to next page
        offset is the offset from the first record of all result
        so offset increase by limit
        self.t_cache > self.offset then read from t_cache
        otherwise read from self.result
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'next')
#    import pdb
#    pdb.set_trace()
    DB.next()

def prev(self, arg = None):
    """
    move to previous page
        offset decreased by limit if capable, otherwise the first page
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'prev')
    DB.prev()

def migrate(self, arg):
    """migrate destination_url"""
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'migrate')
    if not db_ready():
        return
    DB.migrate(db_alias(), arg)

def mydb(self, arg):
    """list out DBs currently connected to"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'mydb')
    if len(DB.db_type.keys()):
        _msg = "You are connected to the following DBs:"
        msg = _msg + "\n" + "-"*len(_msg)
        DBPRINT.print_blue(msg)
        for key in DB.db_type.keys():
            DBPRINT.print_green("%s (%s back-end)" % (key, DB.db_type[key]))
    else:
        DBPRINT.print_red("No DB connection found.")

def alias(self, arg):
    """
    set the new alias to magic
    *alias alias1 string*
    alias1 is added into magic command
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'alias')
    name, fstring = arg.split(" ", 1)
    print "new alias: %s <%s>" % (DBPRINT.msg_green(name), fstring)
    __alias_table__[name] = fstring
    func, params = fstring.split(" ", 1)
    def afunc(self, arg):
        """replacing func"""
        DBPRINT.print_blue(fstring)
        IP.magic("%%%s" % fstring)
    IP.expose_magic(name, afunc)

def dbhelp(self, arg):
    """list out custom magic command"""
    cmd_list = CMDDICT.keys()
    cmd_list.sort()
    sep = 0
    for i in cmd_list:
        if sep < len(str(i)):
            sep = len(str(i))
    if  not arg:
        msg = "Available commands:\n"
        for cmd in cmd_list:
            msg += "%s%s %s\n" % (DBPRINT.msg_green(cmd),
                 " "*abs(sep-len(cmd)), CMDDICT[cmd])
    else:
        cmd = arg.strip()
        if CMDDICTEXT.has_key(cmd):
            msg = "\n%s: %s\n" % (DBPRINT.msg_green(cmd), CMDDICTEXT[cmd])
        else:
            msg = DBPRINT.msg_red("\nSuch command is not available\n")
    print msg

def source(self, arg):
    """execute the SQL queries in the file"""
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'source')
    if not db_ready():
        return
    file1 = None
    try:
        file1 = open(arg, 'r')
    except:
        msg = "No such file '%s'" % arg
        raise DBPRINT.msg_red(msg)
    q_list = file1.read().split(';')
    for query1 in q_list:
        query = query1.replace('\n', ' ').replace(";", "")
        if not query.strip():
            continue
        DBPRINT.print_blue(query)
        DB.execute(query, db_alias())

def format(self, arg):
    """set format of dbmanager print method"""
    if arg == '':
        DBPRINT.print_blue('Current format is %s' % DB.print_method)
        return
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'format')
    if not db_ready():
        return
    if not (arg.lower() == "txt" or arg.lower() == "xml" or
           arg.lower() == "html" or arg.lower() == "csv"):
        raise DBPRINT.msg_red( \
           "ERROR: not supported format, please use txt,xml,html,csv")
    DB.print_method = arg

def plot(self, arg):
    """plot the result of query"""
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'plot')
    if not db_ready():
        return
    DB.plot(db_alias(), arg)

def schema(self, arg):
    """
    1. *schema help* #show help
    2. *schema* #print DDL
    3. *schema graph* #write_graph
    4. *schema > file* #dump database
    """
    if arg.lower() == 'help':
        return dbhelp(self, 'schema')
    if not db_ready():
        return
    if arg == '':
        DB.dump(db_alias())
        return
    a_list = arg.split()
    if a_list[0] == "graph":
        formats = None
        if len(a_list) > 1:
            formats = a_list[1]
        DB.write_graph(db_alias(), formats)
    elif a_list[0] == ">":
        DB.dump(db_alias(), a_list[1])

#
# Immitate SQL statements
#
def select(self, arg):
    """SQL select
    1. *select help*
    2. *select query*, set results
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'select')
    if not db_ready():
        return
    res = DB.execute("select " + arg.replace(";", ""), db_alias())
    result = DB.print_result(res, "select " + arg)
#    RESULTS.set(result)
#    return RESULTS

def insert(self, arg):
    """SQL insert
    1. *insert help*
    2. *insert query*
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'insert')
    if not db_ready():
        return
    DB.execute("insert "+arg.replace(";", ""), db_alias(), list_results = 0)

def drop(self, arg):
    """SQL drop
    1. *drop help*
    2. *drop table*
    3. *drop database*
    4. *drop x* send to database, do reconnect
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'drop')
    if not db_ready():
        return
    params = arg.replace(";", "").split()
    if params[0].lower() == "table":
        DB.drop_table(db_alias(), params[1])
    elif params[0].lower() == "database":
        DB.drop_db(db_alias())
    else:
        DB.execute("drop "+arg.replace(";", ""), db_alias(), list_results = 0)
        DB.reconnect(db_alias(), reload_tables = 1)
    msg = "'%s' executed successfully" % ("drop "+arg, )
    DBPRINT.print_green(msg)

def update(self, arg):
    """SQL update
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'update')
    if not db_ready():
        return
    DB.execute("update "+arg.replace(";", ""), db_alias(), list_results = 0)

def create(self, arg):
    """SQL create
    *create help*
    *create x* send to database, do reconnect to force loading schema
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'create')
    if not db_ready():
        return
    DB.execute("create "+arg.replace(";", ""), db_alias(), list_results = 0)
    DB.reconnect(db_alias())
    msg = "'%s' executed successfully" % ("create "+arg, )
    DBPRINT.print_green(msg)

def alter(self, arg):
    """SQL alter
    *alter help*
    *alter x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'alter')
    if not db_ready():
        return
    DB.execute("alter "+arg.replace(";", ""), db_alias(), list_results = 0)

def set(self, arg):
    """SQL set
    *set help*
    *set x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'set')
    if not db_ready():
        return
    DB.execute("set "+arg.replace(";", ""), db_alias(), list_results = 0)

def rollback(self, arg):
    """SQL rollback
    *rollback help*
    *rollback x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'rollback')
    if not db_ready():
        return
    DB.execute("rollback "+arg.replace(";", ""), db_alias(), list_results = 0)

def begin(self, arg):
    """SQL begin
    *begin help*
    *begin x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'begin')
    if not db_ready():
        return
    DB.execute("begin "+arg.replace(";", ""), db_alias(), list_results = 0)

def commit(self, arg):
    """SQL commit
    *commit help*
    *commit x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'commit')
    if not db_ready():
        return
    DB.execute("commit "+arg.replace(";", ""), db_alias(), list_results = 0)

def explain(self, arg):
    """SQL explain
    *explain help*
    *explain x* send to database
    """
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'explain')
    if not db_ready():
        return
    result = DB.execute("explain "+arg.replace(";", ""), db_alias())
    DB.print_result(result, arg)

#
# QueryBuilder function
#

def find(self, arg):
    """Execute QL expressions"""
    if arg == '' or arg.lower() == 'help':
        return dbhelp(self, 'find')
    if qb_ready():
        return
    query = "find " + arg.split(';')[0].strip()
    mquery = QB.build_query(query)
    if mquery == None:
        _LOGGER.debug("failed to build query %s" % query)
        return
    _LOGGER.info(mquery)
    if not db_ready():
        return
    res = DB.execute(mquery, db_alias())
    result = DB.print_result(res, mquery)
#    RESULTS.set(result)

def mapfile(self, arg):
    """Set map file for QueryBuilder"""
    if arg == '':
        if FILE_DICT['MAP_FILE']:
            DBPRINT.print_blue('Current MAP_FILE is %s' % \
                       FILE_DICT['MAP_FILE'])
        else:
            DBPRINT.print_red('No map file is loaded')
        return
    if arg.lower() == 'help':
        return dbhelp(self, 'mapfile')
    if os.path.isfile(arg):
        FILE_DICT['MAP_FILE'] = arg
        QB.set_mapper(FILE_DICT['MAP_FILE'])
        if db_ready:
            if DB.db_type[db_alias()] == 'mysql':# for mysql case sensitive
                DBPRINT.print_blue('mysql case sensitive')
                QB.mapper.set_sens(True)
            QB.recognize_schema(DB, db_alias)
        return

def schemafile(self, arg):
    """Set schemafile for QueryBuilder"""
    if arg == '':
        if FILE_DICT['SCHEMA_FILE']:
            DBPRINT.print_blue('Current SCHEMA_FILE is %s' % \
                          FILE_DICT['SCHEMA_FILE'])
        else:
            DBPRINT.print_red('No schema file is loaded')
        return
    if arg.lower() == 'help':
        return dbhelp(self, 'schemafile')
    if os.path.isfile(arg):
        FILE_DICT['SCHEMA_FILE'] = arg
        QB.set_from_files(FILE_DICT['SCHEMA_FILE'])

#
# Main function
#
def main():
    """main function to set magic command"""
    option = IP.options
    IP.expose_magic('connect', connect)

    # SQL commands
    IP.expose_magic('select', select)
    IP.expose_magic('SELECT', select)
    IP.expose_magic('insert', insert)
    IP.expose_magic('INSERT', insert)
    IP.expose_magic('drop', drop)
    IP.expose_magic('DROP', drop)
    IP.expose_magic('update', update)
    IP.expose_magic('UPDATE', update)
    IP.expose_magic('create', create)
    IP.expose_magic('CREATE', create)
    IP.expose_magic('alter', alter)
    IP.expose_magic('ALTER', alter)
    IP.expose_magic('set', set)
    IP.expose_magic('SET', set)
    IP.expose_magic('rollback', rollback)
    IP.expose_magic('ROLLBACK', rollback)
    IP.expose_magic('begin', begin)
    IP.expose_magic('BEGIN', begin)
    IP.expose_magic('commit', commit)
    IP.expose_magic('COMMIT', commit)
    IP.expose_magic('explain', explain)
    IP.expose_magic('EXPLAIN', explain)

    IP.expose_magic('close', close)
    IP.expose_magic('rerun', rerun)
    IP.expose_magic('dbhelp', dbhelp)
    IP.expose_magic('show', show)
    IP.expose_magic('desc', desc)
    IP.expose_magic('page', page)
    IP.expose_magic('next', next)
    IP.expose_magic('prev', prev)
    IP.expose_magic('migrate', migrate)
    IP.expose_magic('mydb', mydb)
    IP.expose_magic('alias', alias)
    IP.expose_magic('source', source)
    IP.expose_magic('format', format)
    IP.expose_magic('plot', plot)
    IP.expose_magic('schema', schema)

    IP.expose_magic('find', find)
    IP.expose_magic('mapfile', mapfile)
    IP.expose_magic('schemafile', schemafile)

    # autocall to "full" mode (smart mode is default, I like full mode)
    option.autocall = 2

    # Jason Orendorff's path class is handy to have in user namespace
    # if you are doing shell-like stuff
    try:
        IP.ex("from path import path" )
    except ImportError:
        pass

    IP.ex('import os')

    # Set dbsh prompt
    option.prompt_in1 = 'dbsh |\#> '
    option.prompt_in2 = 'dbsh> '
    option.prompt_out = '<\#| '

    # define dbsh banner
#    ver = "%s.%s" % (dbsh.__version__, dbsh.__revision__)
    ver = "pydbquery_version"
    pyver = sys.version.split('\n')[0]
    ipyver = Release.version
    msg = "Welcome to dbsh %s!\n[python %s, ipython %s]\n%s\n" % \
                                (ver, pyver, ipyver, os.uname()[3])
    msg += "For dbsh help use " + DBPRINT.msg_blue("dbhelp") + \
                             ", for python help use help commands\n"
    option.banner = msg
    option.prompts_pad_left = "1"
    # Remove all blank lines in between prompts, like a normal shell.
    option.separate_in = "0"
    option.separate_out = "0"
    option.separate_out2 = "0"

main()

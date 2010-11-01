#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""ipython profile for db shell"""
# system modules
import os
import sys
#import time
#import types
#import string
#import popen2
import traceback

# ipython modules
from IPython import Release
import IPython.ipapi
IP = IPython.ipapi.get()

from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.dbsh.dbprint import PrintOutput
from pyquerybuilder.dbsh.dbresults import Results    
from pyquerybuilder.dbsh.dbcmd import CMDDICT
from pyquerybuilder.dbsh.dbcmd import CMDDICTEXT
from pyquerybuilder.qb.pyqb import QueryBuilder

#MAP_FILE = None
RESULTS = Results()
#SCHEMA_FILE = None
__alias_table__ = {}
FILE_DICT = {'MAP_FILE':None, 'SCHEMA_FILE':None}

try:
    DB = DBManager()
    DBPRINT = PrintOutput()
    QB = QueryBuilder()
#    FILE_DICT['MAP_FILE'] = os.getenv('HOME')+'/.ipython/map.yaml'
#    QB.set_mapper(FILE_DICT['MAP_FILE'])
except:
    traceback.print_exc()
    raise Exception, "ERROR: fail to load DBManager"


def db_ready():
    """check whether db is connected"""
    if DB.con == None:
        print "This function is not available until you connect to DB"
        return 1
    if DB.con.closed:
        print "This function is not available until you connect to DB"
        return 1
    return 0

def qb_ready():
    """
    Check whether Schema is loaded into QueryBuilder
    1. It can be loaded from DB when DB is connected, after loaded no matter
       DB is connected or closed, QueryBuilder can work
    2. It can be loaded from Schema file.
    Check mapper is ready:
    1. mapfile is loaded 
    2. mapper initialized without error
    """
    if not QB.is_ready():
        print """This function is not avaliable till you: 
                 1. schema loaded to QB, either from DB or from schema file
                 2. map file loaded.
              """
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
    1. connect to database
    2. set prompt
    3. load schema to QueryBuilder
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'close')
    DB.connect(arg)
    set_prompt(DB.dbname(arg))
    tables = DB.load_tables(db_alias())
    QB.set_from_tables(tables)

def close(self, arg):
    """
    1. close database connection
    2. set prompt back to dbsh
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'close')
    if db_ready(): 
        return
    DB.close(db_alias())
    set_prompt('dbsh |\#> ')
    if FILE_DICT['SCHEMA_FILE'] == None :
        return
    if os.path.isfile(FILE_DICT['SCHEMA_FILE']):
        QB.set_from_files(FILE_DICT['SCHEMA_FILE'])
        print 'QB Switch back to Schema file %s' % FILE_DICT['SCHEMA_FILE']

def rerun(self, arg):
    """re-run last command"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'rerun')
    IP.ex("exec _i%d" % int(arg))

def show(self, arg):
    """
    show command, show arg (;)
         show tables will return by our show_table function
         show x send to database
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'show')
    if db_ready(): 
        return
    arg = arg.replace(";","")
    if arg == 'tables':
        DB.show_table(db_alias())
    else:
        DB.execute("show ", db_alias())

def desc(self, arg):
    """desc table"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'desc')
    if db_ready(): 
        return
    DB.desc(db_alias(), arg.replace(";",""))

def page(self, arg):
    """
    page by inputing offset and limit per page
           page(offset,limit)
           page(limit)
    """
    if arg and arg.lower() == 'help':
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
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'migrate')
    if db_ready(): 
        return
    DB.migrate(db_alias(), arg)

def mydb(self, arg):
    """list out DBs currently connected to"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'mydb')
    if len(DB.db_type.keys()):
        _msg = "You are connected to the following DBs:"
        msg = _msg + "\n" + "-"*len(_msg)
        print msg
        for key in DB.db_type.keys():
            print "%s (%s back-end)" % (key, DB.db_type[key])    
    else:
        print "No connection found."

def alias(self, arg):
    """
    set the new alias to magic
    alias1 string
    alias1 is added into magic command
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'alias')
    name, fstring = arg.split(" ", 1)
    print "new alias: %s <%s>" % (DBPRINT.msg_green(name), fstring)
    __alias_table__[name] = fstring
    func, params = fstring.split(" ", 1)
    def afunc(self, arg):
        """replacing func"""
        print fstring
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
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'source')
    if db_ready(): 
        return
    file1 = None
    try:
        file1 = open(arg, 'r')
    except:
        msg = "No such file '%s'" % arg
        raise msg
    q_list = file1.read().split(';')
    for query1 in q_list:
        query = query1.replace('\n', ' ').replace(";", "")
        if not query.strip(): 
            continue
        print query
        DB.execute(query, db_alias())

def format(self, arg):
    """set format of dbmanager print method"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'format')
    if db_ready(): 
        return
    if not (arg.lower() == "txt" or arg.lower() == "xml" or 
           arg.lower() == "html" or arg.lower() == "csv"):
        raise DBPRINT.msg_red( \
           "ERROR: not supported format, please use txt,xml,html,csv")
    DB.print_method = arg
    
def plot(self, arg):
    """plot the result of query"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'plot')
    if db_ready(): 
        return
    DB.plot(db_alias(), arg)
    
def schema(self, arg):
    """
    schema dump database
    schema graph write_graph
    schema > file dump database
    """
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'schema')
    if db_ready(): 
        return
    a_list = arg.split()
    if  not arg:
        DB.dump(db_alias(), arg)
    elif a_list[0] == "graph":
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
    select help
    select query, set results
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'select')
    if db_ready(): 
        return
    res = DB.execute("select " + arg.replace(";", ""), db_alias())
    result = DB.print_result(res, "select " + arg)
    RESULTS.set(result)
#    return RESULTS

def insert(self, arg):
    """SQL insert
    insert help
    insert query
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'insert')
    if db_ready(): 
        return
    DB.execute("insert "+arg.replace(";", ""), db_alias(), list_results = 0)

def drop(self, arg):
    """SQL drop
    drop help
    drop table
    drop database
    drop x send to database, do reconnect
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'drop')
    if db_ready(): 
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
    print DBPRINT.msg_green(msg)

def update(self, arg):
    """SQL update
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'update')
    if db_ready(): 
        return
    DB.execute("update "+arg.replace(";", ""), db_alias(), list_results = 0)

def create(self, arg):
    """SQL create
    create help
    create x send to database, do reconnect
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'create')
    if db_ready(): 
        return
    DB.execute("create "+arg.replace(";", ""), db_alias(), list_results = 0)
    DB.reconnect(db_alias())
    msg = "'%s' executed successfully" % ("create "+arg, )
    print DBPRINT.msg_green(msg)

def alter(self, arg):
    """SQL alter
    alter help
    alter send to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'alter')
    if db_ready(): 
        return
    DB.execute("alter "+arg.replace(";", ""), db_alias(), list_results = 0)

def set(self, arg):
    """SQL set
    set help
    set send to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'set')
    if db_ready(): 
        return
    DB.execute("set "+arg.replace(";", ""), db_alias(), list_results = 0)

def rollback(self, arg):
    """SQL rollback
    rollback help
    set rollback to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'rollback')
    if db_ready(): 
        return 
    DB.execute("rollback "+arg.replace(";", ""), db_alias(), list_results = 0)

def begin(self, arg):
    """SQL begin
    begin help
    begin send to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'begin')
    if db_ready(): 
        return
    DB.execute("begin "+arg.replace(";", ""), db_alias(), list_results = 0)

def commit(self, arg):
    """SQL commit
    commit help
    commit send to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'commit')
    if db_ready(): 
        return
    DB.execute("commit "+arg.replace(";", ""), db_alias(), list_results = 0)

def explain(self, arg):
    """SQL explain
    explain help
    explain send to database
    """
    if arg and arg.lower() == 'help': 
        return dbhelp(self, 'explain')
    if db_ready(): 
        return
    DB.execute("explain "+arg.replace(";", ""), db_alias())

#
# QueryBuilder function
#

def execute(self, arg):
    """Execute QL expressions"""
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'execute')
    if qb_ready():
        return 
    query = arg.split(';')[0].strip()
    mquery = QB.build_query(query)
    print mquery
    if db_ready():
        return 
    res = DB.execute(mquery, db_alias())
    result = DB.print_result(res, mquery)
    RESULTS.set(result)
    
def mapfile(self, arg):
    """Set map file for QueryBuilder"""
    if arg == '':
        print 'current map file is ', FILE_DICT['MAP_FILE']
        return 
    if arg and arg.lower() == 'help':
        return dbhelp(self, 'mapfile')
    if os.path.isfile(arg):
        FILE_DICT['MAP_FILE'] = arg
        QB.set_mapper(FILE_DICT['MAP_FILE'])
        return 

def schemafile(self, arg):
    """set schema file for QueryBuilder"""
    if arg == '': 
        if FILE_DICT['SCHEMA_FILE']:
            print 'Current SCHEMA_FILE is ', FILE_DICT['SCHEMA_FILE']
        else:
            print 'No schema file is loaded'
        return 
    if arg and arg.lower() == 'help':
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
 
    IP.expose_magic('execute', execute)
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

#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
DBManager module
"""
__revision__ = "$Id: $"
__version__ = "$Revision: $"
__author__ = "Valentin Kuznetsov"

# system modules
import sys
import time
import types
import traceback

import os
import thread

# SQLAlchemy modules
import sqlalchemy
from sqlalchemy import asc, desc, text

# local modules
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.dbsh.dbprint import PrintOutput
from pyquerybuilder.dbsh.utils import fetch_from_to

def print_list(input_list, msg = None):
    """Print input list"""
    if  msg:
        s_msg = "-" * len(msg)
        print msg
        print s_msg
    for item in input_list:
        print item

#def print_table(t_list, o_list, l_list, msg = None):
#    """Distribute discription of this table to diff method"""
#    if  msg:
#        print msg
#    print t_list
#    for idx in xrange(0, len(o_list)):
#        print o_list[idx]

def get_graph(sorted_tables, table_index, graph):
    """get graph"""
    index = 0
    for table in sorted_tables:
        name = table.name

        c_names = [col.name for col in table.c]
        for col_name in c_names:
            if table.c[col_name].foreign_keys:
                for fk_table in table.c[col_name].foreign_keys:
                    fk_name = fk_table.target_fullname
                    if fk_name.count('.') == 2:
                        fk_tbname = fk_name.split('.')[1]
                    else:
                        fk_tbname = fk_name.split('.')[0]
                    # 1. fk to him self
                    if fk_tbname == name:
                        continue
                    # 1-1. for dropped table
                    if not table_index.has_key(fk_tbname):
                        continue
                    # 2. duplicate fk to a table
                    if index in graph[table_index[fk_tbname]]:
                        continue
                    graph[table_index[fk_tbname]].append(index)
        index = index + 1

def topo_sort(graph):
    """find node which in degree = 0"""
    visit = {}
    finish = {}
    indegree = {}
    for node in range(0, len(graph)):
        visit[node] = 0
        indegree[node] = 0
    for node in graph:
        for vert in node:
            indegree[vert] = 1
#    for node in range(0, len(graph)):
#        if indegree[node] == 0:
#            print "indegree 0 is ", node
    timer = [0]
    for node in range(0, len(graph)):
        if visit[node] == 0 and indegree[node] == 0:
            dfs_visit(graph, node, timer, visit, finish)
    sequence = []
    for node in finish:
        if len(sequence) ==  0:
            sequence.append(node)
            continue
        if finish[node] > finish[sequence[0]]:
            sequence.insert(0, node)
        elif finish[node] < finish[sequence[-1]]:
            sequence.append(node)
        else:
            for count in range(0, len(sequence)):
                if finish[node] >= finish[sequence[count]]:
                    sequence.insert(count, node)
                    break

#    print "sequence is ", sequence
    return sequence

def dfs_visit(graph, node, timer, visit, finish):
    """DFS visit"""
    visit[node] = 1
    timer[0] = timer[0] + 1
    for adj in graph[node]:
        if visit[adj] == 0:
            dfs_visit(graph, adj, timer, visit, finish)
    visit[node] = 2
    timer[0] = timer[0] + 1
    finish[node] = timer[0]

class DBManager(object):
    """
    A main class which allows access to underlying RDMS system.
    It is based on SQLAlchemy framework, see
    http://www.sqlalchemy.org
    """
    def __init__(self, verbose = 0):
        """
        Constructor.
        """
        self.verbose     = verbose
        self.members     = ['engine', 'db_tables', 'table_names',
                            'db_type', 'db_owner', 'db_schema',
                            'meta_dict', 'drivers', 'aliases']
        # for print_table
        self.print_mgr   = PrintOutput()
        self.print_method = "txt"
        # for plot
        self.formats     = ['jpg', 'png', 'gif', 'svg', 'ps']
        # for fetch_from_to
        self.limit       = None
        self.offset      = None
        self.results     = None
        self.query       = ""
        self.new_paged   = 0
        # for web dynamic table 
        self.t_result = [] # titles of current result
        self.l_result = 0 # total length of current reuslt
        # all parameters below are defined at run time
        self.t_cache     = []
        self.total_cache = {}
        self.query_cache = {}
        self.engine      = {}
        self.db_tables   = {}
        self.table_names = {}
        self.db_type     = {}
        self.db_owner    = {}
        self.db_schema   = {}
        self.meta_dict   = {}
        self.drivers     = {}
        self.aliases     = {}
        self.con         = None

    def write_graph(self, db_alias, format_l=None):
        """
        Write graph of DB schema to db_alias.dot file
        Using dot in shell to create result in given format
        """
        file_name = "%s.dot" % db_alias
        if  self.verbose:
            print "Writing graph of DB schema to", file_name
        dot = DotGraph(file(file_name, "w"))
        # load all tables before building a graph
        t_dict = self.load_tables(db_alias)
        if  self.verbose:
            print t_dict
        for key in t_dict.keys():
            table = t_dict[key]
            table_name = key
            f_keys = table.foreign_keys
            for f_key in f_keys:
                right = f_key.column.table.name
                if right != 'person': # exclude person table
                    dot.add_edge(table_name, right)
        dot.finish_output()
        if  format_l:
            if  format_l not in self.formats:
                msg = "Unsupported format '%s', please use %s" \
                       % (format_l, str(self.formats))
                raise Exception, msg
            cmd = "dot -v -T%s -O %s" % (format_l, file_name)
            try:
                status = os.system(cmd)
                print "Executing", cmd
            except Error:
                print "Fail to execute %s " % cmd , status
                print "Please verify that you have dot installed on your system"
                print traceback.print_exc()


    def dbname(self, arg):
        """
        Generate dbname as corresponding db_type in arg
        """
        if self.drivers.has_key(arg):
            arg = self.drivers[arg]
        db_type, db_name, _, _, host, _, owner, file_name = \
                             self.parse(arg)
        if db_type.lower() == 'oracle':
            name = db_name
            if owner:
                name += "-%s" % owner
            return "%s-%s |\#> " % (db_type, name)
        if db_type.lower() == 'mysql':
            return "%s-%s-%s |\#> " % (db_type, db_name, host)
        if db_type.lower() == 'postgresql':
            return "%s-%s-%s |\#> " % (db_type, db_name, host)
        if db_type.lower() == 'sqlite':
            f_name = file_name.split("/")[-1]
            return "%s-%s |\#> " % (db_type, f_name)
        return "%s-%s |\#> " % (db_type, db_name)

    def show_table(self, db_alias):
        """
        Print out list of tables in DB
        """
        if  self.table_names.has_key(db_alias):
            tables = self.table_names[db_alias]
            tables.sort()
#            if  self.verbose:
            print_list(tables, "\nFound tables:")
        else:
#            if  self.verbose:
            print_list([]," \nFound tables")

    def plot(self, db_alias, query):
        """plot result of query, which is a 2-dimensional data in a thread.
           It will throw exception if the result is more than 3-dimens."""
        try:
            result = self.con.execute(query)
        except:
            raise traceback.print_exc()
        x_list  = []
        y_list  = []
        t_list  = []
        for item in result:
            if type(item) is types.StringType:
                raise Exception, item + "\n"
            if not t_list:
                t_list = list(item.keys())
            if len(item) != 2:
                raise Exception, "Plot support only 2-dimensional data"
            x_val, y_val = item
            x_list.append(x_val)
            y_list.append(y_val)
        thread.start_new_thread(self.pylab_plot,
                               (x_list, y_list, t_list, query))

    def pylab_plot(self, x_list, y_list, t_list, title):
        """plot 2-dimensional data x,y under title[0,1] using pylab library"""
        import pylab
        pylab.plot(x_list, y_list)
        pylab.xlabel(t_list[0])
        pylab.ylabel(t_list[1])
        pylab.title(title)
        pylab.grid(True)
        pylab.show()


    def desc(self, db_alias, table):
        """
        Describe a table from DB
        """
        tables = self.load_tables(db_alias, table) # load table from DB
        if  self.verbose:
            print tables
        tab_obj = tables[table]
        if  self.verbose:
            print "table object:", tab_obj
        t_list = ['Name', 'Type', 'Key', 'Default',
                  'Autoincrement', 'Foreign Keys']
        o_list = [] # contains tuple of values for t_list
        l_list = [len(x) for x in t_list] # column width list
        for col in tab_obj.columns:
            key   = ""
            if col.unique:
                key = "unique"
            elif col.primary_key:
                key = "primary"
            value = "NULL"
            if col.default:
                value = col.default
            f_keys = ""
            for f_key in col.foreign_keys:
                f_keys += "%s " % f_key.column
            v_list = (col.name, col.type, key, value, col.autoincrement, f_keys)
            o_list.append(v_list)
            for idx in xrange(0, len(v_list)):
                if l_list[idx] < len(str(v_list[idx])):
                    l_list[idx] = len(str(v_list[idx]))
        o_list.sort()
#        if  self.verbose:
        self.print_table(t_list, o_list, l_list)
        return len(o_list)

    def dump(self, db_alias, file_name = None):
        """
        Try to create a table and dump results in provided file
        """
        tables = self.load_tables(db_alias)
        # load all tables from DB in order to dump DDL
#        db_type = self.db_type[db_alias]
#        msg    = "--\n-- Dump %s.\n-- %s\n" % \
#              (db_alias, makeTIME(time.time()))
        msg = "--\n-- Dump %s.\n-- %s\n" % (db_alias, time.time())
        if  file_name:
            l_file = open(file_name, 'w')
            l_file.write(msg)
        else:
            if  self.verbose:
                print msg
        for t_name in tables.keys():
            table = tables[t_name]
            try:
                table.create()
            except :
                error = sys.exc_info()[1]
                if  file_name:
                    l_file.write("%s;\n" % error.statement)
                else:
                    print "%s;\n" % error.statement
            try:
                query = "SELECT * FROM %s" % t_name
                if self.db_type[db_alias] == 'oracle' and \
                    self.db_owner[db_alias]:
                    query = "SELECT * FROM %s" % \
                        self.db_owner[db_alias].lower() + '.' + t_name
                result = self.con.execute(query)
                for item in result:
                    if type(item) is types.StringType:
                        raise Exception, item + "\n"
                    columns = str(item.keys()).replace("[", \
                                        "(").replace("]", ")")
                    values  = str(item.values()).replace("[", \
                                       "(").replace("]", ")")
                    stm = "INSERT INTO %s %s VALUES %s;" % \
                             (t_name, columns, values)
                    if self.db_type[db_alias] == 'oracle' and \
                        self.db_owner[db_alias]:
                        stm = "INSERT INTO %s %s VALUES %s;" % \
                            (self.db_owner[db_alias].lower() + '.' + t_name, \
                            columns, values)
                    if  file_name:
                        l_file.write(stm + "\n")
                    else:
                        if  self.verbose:
                            print stm
            except :
                raise traceback.print_exc()
        if file_name:
            l_file.close()

    def migrate(self, db_alias, arg):
        """
        Migrate schema from db_alias to self.aliases[arg]
        have to follow the contraints sequence in oracle
        """
        tables = self.load_tables(db_alias) # load all tables from DB
        db_con = self.con
        self.connect(arg)
        new_dbalias = self.aliases[arg]
        remote_engine = self.engine[new_dbalias]
        meta = sqlalchemy.MetaData()
        meta.bind = remote_engine
# add topo sort for migrate table
#        sorted_tables = self.meta_dict[db_alias].sorted_tables
        sorted_tables = tables.values()
# fix table.tometadata(meta) error on passing parameters
# in format of unicode string
        for table in sorted_tables:
            kwargs = {}
            for arg, val in table.kwargs.items():
                kwargs[str(arg)] = val
            table.kwargs = kwargs
        if self.verbose:
            print "sorted_tables is ", sorted_tables
            print tables.keys()
        sorted_tb = {}
        table_index = {}
        graph = []
        count = 0
        for table in sorted_tables:
            name = table.name
            sorted_tb[table.name] = table
            table_index[table.name] = count
            count = count + 1
            graph.append([])
        get_graph(sorted_tables, table_index, graph)
        if self.verbose:
            print "graph is ", graph
        sequence = topo_sort(graph)
        con = remote_engine.connect()
        if self.verbose:
            print "sequence is ", sequence
        for index in sequence:
            new_table = sorted_tables[index].tometadata(meta)
            if self.db_type[db_alias] == 'oracle':
                if self.db_owner[db_alias]:
                    new_table.schema = self.db_owner[new_dbalias]
            try:
                new_table.create(bind = remote_engine, checkfirst=True)
            except Exception:
                raise traceback.print_exc()
            if self.verbose:
                print new_table
            query = "SELECT * FROM %s" % sorted_tables[index].name
            if self.db_type[db_alias] == 'oracle' and \
                self.db_owner[db_alias]:
                query = "SELECT * FROM %s" % \
                    self.db_owner[db_alias].lower() + '.' + \
                    sorted_tables[index].name
            print "migrating table %s" % sorted_tables[index].name
            try:
                result = db_con.execute(query)
            except Error:
                print "failed to select %s" % str(query)
                raise traceback.print_exc()
            for item in result:
                if type(item) is types.StringType:
                    raise item + "\n"
                ins = new_table.insert(values = item.values())
                try:
                    con.execute(ins)
                except sqlalchemy.exc.OperationalError:
                    print "failed to insert %s" % str(ins)
                    con.execute(ins)
        con.close()
        if  self.verbose:
            print "The content of '%s' has been successfully migrated to '%s'" \
                      % (db_alias, new_dbalias)
        self.close(new_dbalias)

    def create_alias(self, name, params):
        """Update self.aliases"""
        pass
#        self.aliases[name] = params

    def get_alias(self, driver):
        """get db alias"""
        return self.aliases[driver]

    def execute(self, query, db_alias="", list_results=1):
        """Execute query and print result"""
        self.t_cache = []
        try:
            result = self.con.execute(query)
            self.results = result
        except Error:
            raise Exception
        if not list_results:
            return None
#        if self.verbose:
#            self.print_result(result, query)
#        self.print_result(result, query)
        return result

    def execute_with_slice(self, query, limit, offset, sort_idx, sdir):
        """
        execute query with explicit limit and offset
        """
        query._limit = limit
        query._offset = offset
        if sdir == 'asc':
            query = query.apply_labels()
            query = query.order_by(\
                asc(query.columns[query.c.keys()[sort_idx]]))
        elif sdir == 'desc':
            query = query.apply_labels()
            query = query.order_by(\
                desc(query.columns[query.c.keys()[sort_idx]]))
        try:
            result = self.con.execute(query)
            return self.pack_result(result)
        except Error:
            raise Exception

    def explain_query(self, input):
        """
        explain input to SQL query from dictionary
        """
        qid = hash(input)
        if self.query_cache.has_key(qid):
            return self.query_cache[qid]
        return None

    def set_query_explain(self, input, query):
        """
        record SQL query for input
        """
        qid = hash(input)
        if not self.query_cache.has_key(qid):
            self.query_cache[qid] = query

    def get_total(self, query, mquery):
        """
        check the total rows of given query
        execute ensure updating of get_total
        """
        qid = hash(str(query))
        if self.total_cache.has_key(qid):
            return self.total_cache[qid]
        else:
            total_res = self.execute(\
                mquery.apply_labels().alias().count()).fetchall()
            if total_res != []:
                total = total_res[0][0]
            else:
                total = 0
            self.total_cache[qid] = total
            return self.total_cache[qid]

    def set_total(self, qinput, query):
        """
        update the total rows of given query
        incase never cache results
        """
        total_res = self.execute(\
                query.apply_labels().alias().count()).fetchall()
        if total_res != []:
            total = total_res[0][0]
        else:
            total = 0
        qid = hash(str(qinput))
        if total >= 0 :
            self.total_cache[qid] = total
        return self.total_cache[qid]

    def page(self, arg):
        """page by inputing offset and limit per page
           page(offset,limit)
           page(limit)
        """
        i_list = arg.split()
#        self.new_paged = 1
        if  len(i_list) == 2:
            self.offset = int(i_list[0])
            self.limit = int(i_list[1])
        elif len(i_list) == 1:
            self.limit = int(i_list[0])
            self.offset = 0
        else:
            msg = "ERROR: page support only one or two arguments"
#            msg+= cmdDictExt['page']+"\n"
            raise Exception, msg + "\n"

    def next(self, index=None, suppress=False):
        """
        move to next page
        offset is the offset from the first record of all result
        so offset increase by limit
        self.t_cache > self.offset then read from t_cache
        otherwise if results is open read from self.results
                  if results is closed, return without data
        """
#        if self.new_paged:
#            self.new_paged = 0
#            result = self.t_cache[self.offset : self.offset + self.limit]
#            return self.print_result(result, self.query, suppress)

        new_offset = self.offset + self.limit
        if index != None:
            new_offset = index
        if len(self.t_cache) > new_offset:
            self.offset = new_offset
            result = self.t_cache[self.offset : self.offset + self.limit]
        else:
            if self.results.closed:
                result = self.t_cache[self.offset : self.offset + self.limit]
            else:
                result = self.results
        return self.print_result(result, self.query, suppress)

    def prev(self, suppress=False):
        """
        move to previous page
        offset decreased by limit if capable, otherwise the first page
        """
        new_offset = self.offset - self.limit
        if new_offset > 0:
            self.offset = new_offset
        result = self.t_cache[self.offset : self.offset + self.limit]
        return self.print_result(result, self.query, suppress)

    def pack_result(self, result):
        """
        pack result with limit length
        handle format, int and string acceptable
        return title list and values list
        """
        o_list  = []
        t_list  = []
        l_list  = []
        for item in result:
            if type(item) is types.StringType:
                raise Exception, item + "\n"
            #if not (type(result) is types.ListType):
            #    print item
            if not t_list:
                t_list = list(item.keys())
                l_list = [len(x) for x in t_list]
            v_list = item.values()
            o_list.append(v_list)
            for idx in xrange(0, len(v_list)):
                if l_list[idx] < len(str(v_list[idx])):
                    l_list[idx] = len(str(v_list[idx]))
        return (t_list, o_list)

    def print_result(self, result, query, suppress=False):
        """
        Print result and query
        return query and title list and values list
        """
        o_list  = []
        t_list  = []
        l_list  = []
        #NEW after dbprint
        if self.limit and not (type(result) is types.ListType):
            result = fetch_from_to(result, self.limit, self.offset)
        #END of NEW
        for item in result:
            if type(item) is types.StringType:
                raise Exception, item + "\n"
            #if not (type(result) is types.ListType):
            #    print item
            if not t_list:
                t_list = list(item.keys())
                l_list = [len(x) for x in t_list]
            v_list = item.values()
            o_list.append(v_list)
            for idx in xrange(0, len(v_list)):
                if l_list[idx] < len(str(v_list[idx])):
                    l_list[idx] = len(str(v_list[idx]))
        if not suppress:
            self.print_table(t_list, o_list, l_list, query)
        return (query, t_list, o_list)

    def drop_db(self, db_alias):
        """
        Drop database
        """
        tables = self.load_tables(db_alias)
# add topo sort in drop db
#        sorted_tables = self.meta_dict[db_alias].sorted_tables
        sorted_tables = tables.values()
        sorted_tb = {}
        table_index = {}
        graph = []
        count = 0
        for table in sorted_tables:
            sorted_tb[table.name] = table
            table_index[table.name] = count
            count = count + 1
            graph.append([])
        get_graph(sorted_tables, table_index, graph)
        sequence = topo_sort(graph)
        sequence.reverse()
        for index in sequence:
            print "dropping table %s" % sorted_tables[index].name
            try:
                sorted_tables[index].drop()
            except Error:
                query = ""
                if self.db_type[db_alias] == 'oracle':
                    query = text("DROP TABLE " + sorted_tables[index].name \
                        + " CASCADE constraints")
                elif self.db_type[db_alias] == 'postgresql':
                    query = text("DROP TABLE " + sorted_tables[index].name \
                        + " CASCADE ")
                else:
                    traceback.print_exc()
                self.con.execute(query)

        self.db_tables.pop(db_alias)

#        for t_name in tables.keys():
#            table = tables[t_name]
#            try:
#                table.drop()
#            except Error:
#                traceback.print_exc()
#        self.db_tables.pop(db_alias)

    def drop_table(self, db_alias, table_name):
        """
        Drop table from provided database
        """
        tables = self.load_tables(db_alias, table_name)
        if  tables.has_key(table_name):
            tab_obj = tables[table_name]
            try:
                tab_obj.drop()
            except :
                query = ""
                if self.db_type[db_alias] == 'oracle':
                    query = text("DROP TABLE " + tab_obj.name \
                        + " CASCADE constraints")
                elif self.db_type[db_alias] == 'postgresql':
                    query = text("DROP TABLE " + tab_obj.name \
                        + " CASCADE ")
                else:
                    traceback.print_exc()
                self.con.execute(query)
            try:
                tables.pop(table_name)
            except :
                pass
            try:
#                print self.db_tables
                self.db_tables[db_alias].pop(table_name)
            except :
                pass
            try:
                self.table_names[db_alias].remove(table_name)
            except :
                traceback.print_exc()

    def reconnect(self, db_alias, reload_tables = None):
        """
        Close existing connection and reconnect to database
        """
        self.con.close()
        self.con = self.engine[db_alias].connect()
        if reload_tables:
            self.db_tables = {}
            self.table_names = {}
        self.load_table_names(db_alias)

    def close(self, db_alias):
        """
        Close connection to database
        """
        self.con.close()
        for dict in self.members:
            member = getattr(self, dict)
            if  member.has_key(db_alias):
                try:
                    member.pop(db_alias)
                except Error:
                    pass
#        if self.verbose:
        print "database connection %s has been closed" % \
                 db_alias

    def parse(self, arg):
        """
        Parse provided input to make data base connection.
        SQLAlchemy support the following format :

        .. doctest::

            driver://username:password@host:port/database,

        while here we extend it to the following structure
        (suitable for ORACLE):

        .. doctest::

            driver://username:password@host:port/database:db_owner
        """
        port      = None
        host      = None
        owner     = None
        file_name = None
        db_name   = None
        db_user   = None
        db_pass   = None
        try:
            driver, dbparams = arg.split("://")
        except Error:
            msg = "Fail to parse connect argument '%s'\n" % arg
            # msg += cmdDictExt['connect']
            raise Exception, msg + "\n"
        if  dbparams.find("@") != -1:
            user_pass, rest  = dbparams.split("@")
            db_user, db_pass = user_pass.split(":")
            if  rest.find("/") != -1:
                host_port, dbrest = rest.split("/")
                try:
                    host, port = host_port.split(":")
                except Error:
                    host = host_port
            else:
                dbrest = rest
            try:
                db_name, owner  = dbrest.split(":")
            except :
                db_name = dbrest
        else: # in case of SQLite, dbparams is a file name
            file_name = dbparams
            db_name   = file_name.split("/")[-1]
            if  driver != 'sqlite':
                msg = "'%s' parameter is not supported for driver '%s'" % \
                          (file_name, driver)
                raise Exception, msg + "\n"
        return (driver.lower(), db_name, db_user, db_pass,
                             host, port, owner, file_name)

    def connect(self, driver):
        """Connect to DB"""
        if self.drivers.has_key(driver):
            arg = self.drivers[driver]
        else:
            arg = driver
        db_type, db_name, db_user, db_pass, host, port, db_owner, file_name = \
            self.parse(arg)
        db_schema = None
        if db_type =='oracle' and db_owner:
            db_alias  = '%s-%s-%s' % (db_type, db_name, db_owner)
            db_schema = db_owner.lower()
        elif db_type == 'sqlite':
            db_alias = '%s-%s' % (db_type, db_name)
        else:
            db_alias = db_name
            if db_type:
#                db_alias += "-" + db_type
                db_alias = '%s-%s-%s' % (db_type, db_name, host)
#            print "db_alias: %s"% db_alias
        if  not self.drivers.has_key(driver):
            self.drivers[db_alias] = driver
            self.aliases[driver] = db_alias

        e_type  = str.lower(db_type)
        if  self.verbose:
            print "Connecting to %s (%s back-end), please wait ..." % \
                     (db_alias, db_type)

        # Initialize SQLAlchemy engines
        if  not self.engine.has_key(db_alias):
            e_name = ""
            if port != None:
                host_port = "%s:%s" % (host, port)
            else:
                host_port = host
            if e_type == 'sqlite':
                e_name = "%s://%s?check_same_thread=False" % (e_type, file_name)
                if not file_name.startswith('/'):
                    e_name = "%s:///:memory:%s?check_same_thread=False" % \
                             (e_type, file_name)
                engine = sqlalchemy.create_engine(e_name)
            elif e_type == 'oracle':
                e_name = "%s://%s:%s@%s" % (e_type, db_user, db_pass, db_name)
                engine = sqlalchemy.create_engine(e_name,
                            strategy = 'threadlocal', threaded = True)
            elif e_type == 'mysql':
                e_name = "%s://%s:%s@%s/%s" % (e_type, db_user,
                                          db_pass, host_port, db_name)
                engine = sqlalchemy.create_engine(e_name,
                                 strategy = 'threadlocal')
            elif e_type == 'postgresql':
                e_name = "%s://%s:%s@%s/%s" % (e_type, db_user,
                                           db_pass, host_port, db_name)
                engine = sqlalchemy.create_engine(e_name,
                                 strategy = 'threadlocal')
            else:
                print Exception, "Unsupported DB engine back-end"
            self.engine[db_alias] = engine
        self.con = self.engine[db_alias].connect()
        if  not self.db_type.has_key(db_alias):
            self.db_type[db_alias] = e_type
        if  not self.db_owner.has_key(db_alias) :
            self.db_owner[db_alias] = db_owner
        if  not self.db_schema.has_key(db_alias):
            self.db_schema[db_alias] = db_schema
        if  not self.meta_dict.has_key(db_alias):
            db_meta = sqlalchemy.MetaData()
            db_meta.bind = self.engine[db_alias]
            self.meta_dict[db_alias] = db_meta
        if  not self.table_names.has_key(db_alias):
            self.table_names[db_alias] = self.load_table_names(db_alias)
        return self.con

    def load_table_names(self, db_alias):
        """
        Retrieve table names for provided database name.
        """
        e_type = self.db_type[db_alias]
        engine = self.engine[db_alias]
        if  e_type == 'oracle' and self.db_owner[db_alias]:
            owner = self.db_owner[db_alias].upper()
            query = "SELECT table_name FROM all_tables WHERE owner='%s'" % \
                     owner
            result = self.con.execute(query)
            table_names = [x[0].lower().split(".")[-1] for x in result]
            query = "SELECT view_name FROM all_views WHERE owner='%s'" % \
                    self.db_owner[db_alias].upper()
            result = self.con.execute(query)
            table_names += [x[0].lower().split(".")[-1] for x in result]
        else:
            table_names = engine.table_names()
        return table_names

    def load_tables(self, db_alias, table_name = None):
        """
        Load table objects for provided database. The optional table_name
        parameter allows to load concrete table from the database
        """
        if  self.db_tables.has_key(db_alias):
            tables = self.db_tables[db_alias]
        else:
            tables = {}
        db_meta = self.meta_dict[db_alias]
        e_type = self.db_type[db_alias]
        kwargs = {}
        kwargs = {'autoload':True}
        for t_name in self.table_names[db_alias]:
            tab_name = t_name.lower()
            if e_type == "mysql":
                tab_name = t_name
            if  tables.has_key(tab_name):
                continue
            if  table_name and tab_name != table_name:
                continue
            if  e_type == 'oracle':
#                kwargs['useexisting'] = True
# SQLAlchemy 0.7.5
                kwargs['extend_existing'] = True
            if self.db_owner[db_alias] and e_type == 'oracle':
                kwargs['schema'] = self.db_owner[db_alias].upper()
            tables[tab_name] = sqlalchemy.Table(tab_name, db_meta, **kwargs)
        self.db_tables[db_alias] = tables
        return tables

    def print_table(self, t_list, o_list, l_list, msg=None):
        """Distribute discription of this table to diff method"""
        if self.print_method == "txt":
            self.print_mgr.print_txt(t_list, o_list, l_list, msg)
        elif self.print_method == "xml":
            self.print_mgr.print_xml(t_list, o_list, l_list, msg)
        elif self.print_method == "html":
            self.print_mgr.print_html(t_list, o_list, l_list, msg)
        elif self.print_method == "csv":
            self.print_mgr.print_csv(t_list, o_list, l_list, msg)
        else:
            self.print_mgr.print_txt(t_list, o_list, l_list, msg)


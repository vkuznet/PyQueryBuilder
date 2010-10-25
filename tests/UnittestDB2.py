#!/usr/bin/env python
# $Id: UnittestDB.py,v 1.1 2007/03/22 15:15:04 valya Exp $
"""
This creates a database for unit tests.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

# system modules
import re

from sqlalchemy import MetaData, Column, Table, Integer, ForeignKey
from pyquerybuilder.tools.schema_loader import SchemaLoader
from yaml import load as yamlload
from logging import getLogger


_LOGGER = getLogger("ConstructQuery")

def load_from_file(filename):
    """load from file"""
    udb = UnittestDB()
    return udb.load_from_file(filename)
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
    time = [0]
    for node in range(0, len(graph)):
        if visit[node] == 0 and indegree[node] == 0:
            dfs_visit(graph, node, time, visit, finish)
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

def dfs_visit(graph, node, time, visit, finish):
    """DFS visit"""
    visit[node] = 1
    time[0] = time[0] + 1
    for adj in graph[node]:
        if visit[adj] == 0:
            dfs_visit(graph, adj, time, visit, finish)
    visit[node] = 2
    time[0] = time[0] + 1
    finish[node] = time[0]

    
    

class UnittestDB(object):
    """create DB for Unittest """
    def __init__(self):
        """ initialize"""
        self._metadata = None
        self.ma_table = re.compile("CREATE TABLE (\w+)")
        self.ma_column = re.compile("\s+(\w+)\s+(.*),")
        self.ma_constraint = re.compile("ALTER TABLE\s+(\w+)\s+ADD CONSTRAINT")
        self.ma_foreign = re.compile("key\((\w+)\)\s+references\s+(\w+)\(ID\)")
    
    def create_from(self, d_input):
        """create from input"""
#        metadata = ThreadLocalMetaData()
        # ThreadLocal don't have a engine 
        metadata = MetaData()
        
        for d_tablename in d_input.keys():
            d_table = d_input[d_tablename]
            s_col = []
            s_vals = {}
            for d_col in d_table:
                d_colname = d_col['member']
                _LOGGER.debug("UnittestDB.create_from: adding %s.%s." 
                               % (d_tablename, d_colname))
                if d_col.has_key('foreignKey'):
                    s_col.append(Column(d_colname, Integer,
                                 ForeignKey(d_col["foreignKey"].lower()+".ID")))
                elif d_col.has_key("primaryKey"):
                    s_col.append(Column(d_colname, Integer, primary_key=True))
                else:
                    s_col.append(Column(d_colname, Integer))
                s_vals[d_colname] = 0
            apply(Table, [d_tablename.lower(), metadata] + s_col)
        return metadata

    def column_count(self, metadata):
        """count column"""
        c_count = 0
        for table in metadata.sorted_tables:
#            name = table.name
#            for column in table.c:
#                c_count = c_count + 1
            c_count += sum(1 for _ in table.c)
        return c_count

    def load_from_file(self, filename):
        """create metadata from schema file"""
        schema_file = file(filename)
        schema_yaml = yamlload(schema_file)
        schema_file.close()
        metadata = self.create_from(schema_yaml)
        return metadata

    def fill_table(self, table, idx):
        """fill table with our test data"""
#        print "fill_table %s %d"%( table.name,idx)
        insert_clause = table.insert()
        c_names = [col.name for col in table.c]
        insert_dict = {}
        for col_name in c_names:
            if table.c[col_name].primary_key:
                insert_dict[col_name] = idx
            elif table.c[col_name].foreign_keys:
                insert_dict[col_name] = idx
            else:
                insert_dict[col_name] = idx + 100
#            _LOGGER.debug("insert %s %s" % (table.name, insert_dict))
        insert_clause.execute(insert_dict)
    
    def get_graph(self, sorted_tables, table_index, graph):
        """get graph"""
        index = 0
        for table in sorted_tables:
            name = table.name
            c_names = [col.name for col in table.c]
            for col_name in c_names:
                if table.c[col_name].foreign_keys:
                    fk_table = table.c[col_name].foreign_keys[0]
                    fk_name = fk_table.target_fullname
                    fk_tbname = fk_name.split('.')[0]
                    # 1. fk to him self 
                    if fk_tbname == name:
                        continue
                    # 2. duplicate fk to a table
                    if index in graph[table_index[fk_tbname]]:
                        continue
                    graph[table_index[fk_tbname]].append(index)
            index = index + 1 
#        print "graph is ", graph
        

    def fill_tables(self, metadata, row_cnt):
        """ fill table by row lines test data
        """
        sorted_tables = metadata.sorted_tables
        sorted_tb = {}
        table_index = {}
        graph = []
        count = 0
        for table in sorted_tables:
            sorted_tb[table.name] = table
            table_index[table.name] = count
            count = count + 1
            graph.append([])  
#            print "  ", table.name
        self.get_graph(sorted_tables, table_index, graph)
#        self.get_graph(sorted_tables, sorted_tb, table_index, graph)
#        for index in range(0, len(graph)):
#            for idx in graph[index]:
#                print "%s -> %s" %( sorted_tables[index].name,\
#                        sorted_tables[idx].name)
        sequence = topo_sort(graph)
#        for index in sequence:
#            print index, " ", sorted_tables[index].name
#        print "%s = %s"%(len(sorted_tables),len(sequence))
        for idx in range(0, row_cnt):
            for index in sequence:
                self.fill_table(sorted_tables[index], idx+1)
 


    def load_with_fake_data(self, filename, dbname):
        """load with fake data"""
        udb = UnittestDB()
        if filename.endswith("yaml"):
            metadata = udb.load_from_file(filename)
        elif filename.endswith("sql"):
            metadata = udb.read_from_oracle(filename)
        metadata.bind = dbname
        metadata.drop_all()
        metadata.create_all()
        udb.fill_tables(metadata, 10)
        return metadata

    def read_from_oracle(self, filename = "oracle.sql"):
        """read from oracle"""
#        metadata = ThreadLocalMetaData()
        metadata = MetaData()
        
        file_local = file(filename, "r")
        line = file_local.readline()
        

        
        _begin = 0
        _create = 1
        _constraint = 2
        # tables [table_name] = table_name
        tables = {}
        # f_keys [table_name] = (fkey col, ref table_name)
        f_keys = {}
        state = _begin
        while line:
            if state is _begin:
                table_match = self.ma_table.match(line)
                constraint_match = self.ma_constraint.match(line)
                if table_match:
                    current_table = table_match.group(1)
                    tables[current_table] = []
                    f_keys[current_table] = {}
                    state = _create
                elif constraint_match:
                    current_table = constraint_match.group(1)
                    state = _constraint
            elif state is _create:
                col_match = self.ma_column.match(line)
                if line.find(";") > 0:
                    state = _begin
                elif col_match:
                    col = col_match.group(1)
                    if not col == "primary":
                        tables[current_table].append(col)
            elif state is _constraint:
                foreign_match = self.ma_foreign.search(line)
                if foreign_match:
                    l_col = foreign_match.group(1)
                    right_table = foreign_match.group(2)
                    f_keys[current_table][l_col] = right_table
                state = _begin
            line = file_local.readline()
        file_local.close()
        
        for t_name in tables:
            cols = []
            for col in tables[t_name]:
                if col == "ID":
                    cols.append(Column(col, Integer, primary_key = True))
                elif f_keys[t_name].has_key(col):
                    right_table = f_keys[t_name][col]
                    cols.append(Column(col, Integer,
                                 ForeignKey(right_table + ".ID")))
                else:
                    cols.append(Column(col, Integer))
            apply(Table, [t_name, metadata] + cols)
       
        return metadata


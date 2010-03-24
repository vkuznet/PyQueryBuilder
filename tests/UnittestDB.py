#!/usr/bin/env python
# $Id: UnittestDB.py,v 1.1 2007/03/22 15:15:04 valya Exp $
"""
This creates a database for unit tests.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

# system modules
import re
import unittest

from os import unlink, path
from os import unlink, path
from sqlalchemy import MetaData, Column, Table, Integer, ForeignKey
from yaml import load as yamlload
from logging import getLogger

# local modules
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.WriteSqlAlchemyGraph import write_sql_alchemy_graph

_LOGGER = getLogger("ConstructQuery")

def load_from_file(filename):
    """load from file"""
    udb = UnittestDB()
    return udb.load_from_file(filename)

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
                                 ForeignKey(d_col["foreignKey"]+".ID")))
                elif d_col.has_key("primaryKey"):
                    s_col.append(Column(d_colname, Integer, primary_key=True))
                else:
                    s_col.append(Column(d_colname, Integer))
                s_vals[d_colname] = 0
            apply(Table, [d_tablename, metadata] + s_col)
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

    def fill_tables(self, metadata, row_cnt):
        """ fill table by row lines test data
            PK col idx ++ 
            FK col idx ++
            other col running idx ++"""
        for table in metadata.sorted_tables:
            name = table.name
            insert_clause = table.insert()
            id_idx = 0
            running_idx = 0
            c_names = [col.name for col in table.c]
            inserts = []
            for _ in range(0, row_cnt):
                insert_dict = {}
                for col_name in c_names:
                    if table.c[col_name].primary_key:
                        insert_dict[col_name] = id_idx
                        id_idx = id_idx + 1
                    elif table.c[col_name].foreign_keys:
                        insert_dict[col_name] = ((id_idx + 1) % row_cnt)
                    else:
                        insert_dict[col_name] = running_idx
                    running_idx = running_idx + 1
                _LOGGER.debug("insert %s %s" % (name, insert_dict))
                inserts.append(insert_dict)
                
            insert_clause.execute(inserts)

    def load_with_fake_data(self, filename, dbname):
        """load with fake data"""
        udb = UnittestDB()
        if filename.endswith("yaml"):
            metadata = udb.load_from_file(filename)
        elif filename.endswith("sql"):
            metadata = udb.read_from_oracle(filename)
        metadata.bind = dbname
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

class TestUnittestDB(unittest.TestCase):
    """test UnittestDB"""
    def setUp(self):
        """default"""
        pass

    def tearDown(self):
        """default"""
        pass
            
    def test_sample_query(self):
        """test sample query"""
        db_test = UnittestDB()
#        class zCol(object):
#            """z col"""
#            def __init__(self, prim, fkey):
#                """initialize"""
#                self.primarykey = prim
#                self.foreignkey = fkey
        inputs = { "t0" : [{ "member" : "ID", "primaryKey" : None},
                          {"member" : "zCol"}
                         ],
                  "t1" : [{ "member" : "ID", "primaryKey" : None},
                          { "member" : "who", "foreignKey" : "t0"}
                         ]
                }
        metadata = db_test.create_from(inputs)
        c_count = db_test.column_count(metadata)
        self.assertEqual(c_count, 4)

    def test_from_yaml(self):
        """test from yaml"""
        metadata = load_from_file('starting_db.yaml')
        udb = UnittestDB()
        c_count = udb.column_count(metadata)
        self.assertEqual(c_count, 36)
    
    def test_fill(self):
        """test fill"""
        if path.exists('unittest2.db'):
            unlink('unittest2.db')
        udb = UnittestDB()
        metadata = udb.load_from_file('starting_db.yaml')
#        for table in metadata.sorted_tables:
#            print table.name
#            for col in table.columns:
#                print col
        metadata.bind = 'sqlite:///unittest2.db'
        metadata.create_all()
        udb.fill_tables(metadata, 10)
#        metadata.dispose()

    def test_oracle_write(self):
        """test oracle write"""
        udb = UnittestDB()
        metadata = udb.read_from_oracle('oracle.sql')
        dot = DotGraph(file("oracle.dot", "w"))
        write_sql_alchemy_graph(dot, metadata, set(['Person']))
        
    def test_from_oracle(self):
        """test from oracle"""
        if path.exists('unittest2.db'):
            unlink('unittest2.db')
        udb = UnittestDB()
        metadata = udb.read_from_oracle('oracle.sql')
#        for table in metadata.sorted_tables:
#            print table.name
#            for col in table.columns:
#                print col
        metadata.bind = 'sqlite:///unittest2.db'
        metadata.create_all()
        udb.fill_tables(metadata, 10)
#        metadata.dispose()
        
def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUnittestDB))
    return suite
                         
if __name__ == '__main__':
    #import ConfigureLog
    #ConfigureLog.configurelog()
    unittest.TextTestRunner(verbosity=1).run(suite())

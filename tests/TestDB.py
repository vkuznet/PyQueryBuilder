#!/usr/bin/env python
"""
This creates a database for unit tests.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

import unittest
from UnittestDB import UnittestDB
from UnittestDB import load_from_file
from os import unlink, path
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.WriteSqlAlchemyGraph import write_sql_alchemy_graph
from sqlalchemy import MetaData, create_engine

class TestUnittestDB(unittest.TestCase):
    """test UnittestDB"""
    def setUp(self):
        """default"""
        self.inputs = { "a0" : [{ "member" : "ID", "primaryKey" : None},
                          {"member" : "zCol"}
                         ],
                  "a1" : [{ "member" : "ID", "primaryKey" : None},
                          { "member" : "who", "foreignKey" : "a0"}
                         ]
                }
        self.url = 'mysql://cms:passcms@localhost:3306/test'
        self.engine = create_engine(self.url)

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
        connection = self.engine.connect()
        metadata = db_test.create_from(self.inputs)
        metadata.create_all(bind=connection)
        c_count = db_test.column_count(metadata)
        metadata.drop_all(bind=connection)
        self.assertEqual(c_count, 4)
        connection.close()
        

    def test_from_yaml(self):
        """test from yaml"""
        metadata = load_from_file('starting_db.yaml')
        udb = UnittestDB()
        c_count = udb.column_count(metadata)
        self.assertEqual(c_count, 40)

    def test_fill(self):
        """test fill"""
#        if path.exists('unittest2.db'):
#            unlink('unittest2.db')
        udb = UnittestDB()
        metadata = udb.load_from_file('starting_db.yaml')
#        for table in metadata.sorted_tables:
#            print table.name
#            for col in table.columns:
#                print col

        connection = self.engine.connect()
        metadata.bind = connection
        metadata.drop_all()
        for table in metadata.sorted_tables:
            for col in table.columns:
                col.autoincrement = False
        metadata.create_all()
        udb.fill_tables(metadata, 10)
        connection.close()

    def test_oracle_write(self):
        """test oracle write"""
        udb = UnittestDB()
        metadata = udb.read_from_oracle('oracle.sql')
        dot = DotGraph(file("oracle.dot", "w"))
        write_sql_alchemy_graph(dot, metadata, set(['Person']))

    def test_by_sql_file(self):
        """test by sql file"""
        udb = UnittestDB()
        metadata = udb.load_from_file('starting_db.yaml')
        connection = self.engine.connect()
        metadata.bind = connection
        metadata.drop_all()
        connection.close()

        udb = UnittestDB()
        metadata = udb.read_from_oracle('oracle.sql')
#        for table in metadata.sorted_tables:
#            print table.name
#            for col in table.columns:
#                print col
        metadata.bind = self.engine
        metadata.create_all()
        udb.fill_tables(metadata, 10)
        metadata.drop_all()

def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUnittestDB))
    return suite

if __name__ == '__main__':
    #import ConfigureLog
    #ConfigureLog.configurelog()
    unittest.TextTestRunner(verbosity=3).run(suite())


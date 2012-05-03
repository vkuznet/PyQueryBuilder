#!/usr/bin/env python
"""
Test SchemaHandler on Schema object
"""

# system modules
import unittest
import os, logging, sys

from logging import getLogger
from StringIO import StringIO
from sqlalchemy import select

# local modules
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.pyqb import QueryBuilder
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.qb.pyqb import query_parser
from pyquerybuilder.db.DBManager import DBManager
try:
    from UnittestDB import load_from_file, UnittestDB
except :
    pass

class TestQueryBuilder(unittest.TestCase):
    """Test class for Querybuilder"""
    def setUp(self):
        """default"""
        metadata = load_from_file("starting_db.yaml")
        app = QueryBuilder()
        app.set_mapper('testmap.yaml')
        app.set_from_tables(metadata.tables)
        app.recognize_schema() # without loading statistics
        self.app = app


    def tearDown(self):
        """default """
        pass

    def test_query_parser(self):
        """
        test clause generation
        """
        query = "find dataset.createdate, dataset.name where file.name = 123"
        mquery, keylist = query_parser(self.app.mapper, query)
        mquery2 = {'keywords':[['ProcessedDataset.CreateDate'], ['Files.Path']],
                    'constraints': [{'value': '123', 'keyword':
                    ['Files.Name', 'file.name'], 'sign': '='}]}
        keylist2 = {'mkeywords': [['ProcessedDataset.CreateDate'],['Files.Path']],
                        'constraints':['file.name'],
                    'keywords':['dataset.createdate', 'dataset.name']}
        self.assertEqual(mquery['keywords'], mquery2['keywords'])
        self.assertEqual(mquery['constraints'],mquery2['constraints'])
        self.assertEqual(keylist['keywords'], keylist2['keywords'])
        self.assertEqual(keylist['constraints'], keylist2['constraints'])

    def test_single_query(self):
        """
        test single query without constaints
        """
        query = "find dataset.createdate, dataset.name"
        mquery, keylist = query_parser(self.app.mapper, query)
        query = self.app.build_query(query)
        print query

    def test_single_query2(self):
        """
        test single query with constraints
        """
        query = "find dataset.name where file.name = 123 and \
            (dataset.name = 456 or dataset.name = 789)"
        mquery, keylist = query_parser(self.app.mapper, query)
        query = self.app.build_query(query)
        print query

    def test_single_query3(self):
        """test query with multiple tables"""
        query = "find dataset.name, algo.name, primds.name"
        mquery, keylist = query_parser(self.app.mapper, query)
        query = self.app.build_query(query)
        print query
        query = "find dataset.name, algo.name, primds.name where file.name = 123 and \
            (dataset.name = 456 or dataset.name = 789)"
        mquery, keylist = query_parser(self.app.mapper, query)
        query = self.app.build_query(query)
        print query

class TestLive(unittest.TestCase):
    """live test """
    def setUp(self):
        """initialize test sqlite db then metadata"""
        if os.path.exists('unittest.db'):
            os.unlink('unittest.db')
        test_db = UnittestDB()
        metadata = test_db.load_with_fake_data('oracle.sql',
                            'sqlite:///unittest.db')
        self.metadata = metadata
        app = QueryBuilder()
        app.set_mapper('map.yaml')
        app.set_from_tables(metadata.tables)
        app.recognize_schema() # without loading statistics
        self.app = app

    def tearDown(self):
        """release resources"""
        self.metadata.bind.engine.dispose()
        os.unlink('unittest.db')

    def display_rows(self, rows):
        """display rows on LOGGER"""
        for row in rows:
            continue

    def test_read_query(self):
        """test read querys"""
        metadata = self.metadata
        process_dataset = self.app.querybuilder.find_table('ProcessedDataset')
        data_tier = self.app.querybuilder.find_table('DataTier')
        primary_dataset = self.app.querybuilder.find_table('PrimaryDataset')

        # First try a regular select query.
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
            primary_dataset.c.Name], process_dataset.c.ID == 0)
        print "regular select ", select_test
        results = select_test.execute()
        rows = results.fetchall()
        self.display_rows(rows)

        # Then use our software to modify one.
        query = 'find dataset.name, tier.name, primds.name'
        query = self.app.build_query(query)
        print "modified select", query
        select_clause = query
        results = select_clause.execute()
        rows = results.fetchall()
        self.display_rows(rows)
        self.assertEqual(len(rows[0]), 3)

def suite():
    """suite all test together"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryBuilder))
    suite.addTest(unittest.makeSuite(TestLive))
    return suite

if __name__ == '__main__':
#    import ConfigureLog
#    ConfigureLog.configurelog()
#    logging.basicConfig(stream=sys.stderr)
#    logging.getLogger("ConstructQuery").setLevel(logging.DEBUG)
    unittest.TextTestRunner(verbosity=2).run(suite())


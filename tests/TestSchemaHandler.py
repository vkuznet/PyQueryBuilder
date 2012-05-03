#!/usr/bin/env python
"""
Test SchemaHandler on Schema object
"""

# system modules
import unittest
import os, logging, sys

from logging import getLogger
from StringIO import StringIO
from sqlalchemy import select, and_

# local modules
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.SchemaHandler import SchemaHandler
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.qb.pyqb import query_parser
from pyquerybuilder.qb.ConstructQuery import ConstructQuery
try:
    from UnittestDB import load_from_file, UnittestDB
except :
    pass

class TestSchemaHandler(unittest.TestCase):
    """Test class for Querybuilder"""
    def setUp(self):
        """default"""
        metadata = load_from_file("starting_db.yaml")
        self.handler = SchemaHandler(metadata.tables)
        self.mapper = Mapper()
        self.mapper.load_mapfile('testmap.yaml')
        self.mapper.validate_map(metadata.tables)
        self.handler._schema.recognize_type(self.mapper)
        self.handler._schema.handle_alias()
        self.handler._schema.gen_attr_links(self.mapper)
        simschema = self.handler._schema.gen_simschema()
        simschema.update_nodelist()
        graph = simschema.get_wgraph_from_schema()
        self.handler.subconstructors.append(ConstructQuery(graph, weighted=True))
        nodes = set(range(len(simschema.ordered)))
        self.handler.subnodes.append(nodes)
        self.handler._simschema = simschema


    def tearDown(self):
        """default """
        pass

    def test_gen_clauses(self):
        """
        test clause generation
        """
        keylist = {'keywords':['dataset.createdate', 'dataset.name'],
                   'constraints':['file.name'],
                   'keyset':['ProcessedDataset.CreateDate',
                        'Files.Path', 'Files.Name']}
        mquery = {'keywords':[['ProcessedDataset.CreateDate'], ['Files.Path']],
                    'constraints': [{'value': '123', 'keyword':
                                ['Files.Name', 'file.name'],
                                    'sign': '='}]}
        clause = self.handler.gen_clauses(mquery, keylist)
        self.assertEqual(str(clause.left).lower(), 'Files.Name'.lower())

    def test_gen_clauses_comp(self):
        """
        test complex clause generation
        ("Files"."Name" = :Name_1) AND (("Files"."Path" = :Path_1) OR
        ("Files"."Path" = :Path_2))
        """
        mquery = {'keywords': [['Files.Path']],
        'constraints': [{'value': '123', 'keyword': ['Files.Name', 'file.name'], 'sign': '='},
                        'and',
                        [{'value': '456', 'keyword': ['Files.Path', 'dataset'], 'sign': '='},
                            'or',
                         {'value': '789', 'keyword': ['Files.Path', 'dataset'], 'sign': '='}]]}
        keylist = {'keywords':['dataset'],
                    'constraints':['file.name', 'dataset', 'dataset'],
                    'keyset':['Files.Name','Files.Path','Files.Path']}
        clause = self.handler.gen_clauses(mquery, keylist)
        self.assertEqual(str(clause.clauses[0].left).lower(), \
        'Files.Name'.lower())

    def test_single_query(self):
        """
        test single query without constaints
        """
        keylist = {'keywords':['dataset.createdate'],
                    'constraints':None,
                    'keyset':['ProcessedDataset.CreateDate'],
                    'mkeywords':['ProcessedDataset.CreateDate']}
        whereclause = None
        query = self.handler.build_query(whereclause, keylist)
        print query

    def test_single_query2(self):
        """
        test single query with constraints
        """
        mquery = {'keywords': [['Files.Path']],
        'constraints': [{'value': '123', 'keyword': ['Files.Name', 'file.name'], 'sign': '='},
                        'and',
                        [{'value': '456', 'keyword': ['Files.Path', 'dataset'], 'sign': '='},
                            'or',
                         {'value': '789', 'keyword': ['Files.Path', 'dataset'], 'sign': '='}]]}
        keylist = {'keywords':['dataset'],
                    'constraints':['file.name', 'dataset', 'dataset'],
                    'keyset':['Files.Path','Files.Name','Files.Path','Files.Path'],
                    'mkeywords':[['Files.Path']]}
        clause = self.handler.gen_clauses(mquery,keylist)
        query = self.handler.build_query(clause, keylist)
        print query

    def test_single_query3(self):
        """test query with multiple tables"""
        mquery = {'keywords': [['Files.Path'], ['ProcAlgo.Algorithm'],
        ['PrimaryDataset.Name']]}
        keylist = {'keywords': ['dataset', 'algo', 'primds'],
                    'constraints': [],
                    'mkeywords':[['Files.Path'],['ProcAlgo.Algorithm'],['PrimaryDataset.Name']],
                    'keyset':['Files.Path','ProcAlgo.Algorithm','PrimaryDataset.Name']}

        clause = self.handler.gen_clauses(mquery,keylist)
        query = self.handler.build_query(clause, keylist)
        print query
        mquery = {'keywords': [['Files.Path'], ['ProcAlgo.Algorithm'],
                                ['PrimaryDataset.Name']],
                        'constraints':
                        [{'value': '123', 'keyword': ['Files.Name', 'file.name'], 'sign': '='},
                        'and',
                        [{'value': '456', 'keyword': ['Files.Path', 'dataset'], 'sign': '='},
                            'or',
                         {'value': '789', 'keyword': ['Files.Path', 'dataset'], 'sign': '='}]]}
        keylist = {'keywords': ['dataset', 'algo', 'primds'],
                    'constraints': ['file.name', 'dataset', 'dataset'],
                    'keyset':['Files.Path',
                        'ProcAlgo.Algorithm','PrimaryDataset.Name',
                        'Files.Name', 'Files.Path', 'Files.Path'],
                    'mkeywords':[['Files.Path'],
                    ['ProcAlgo.Algorithm'],['PrimaryDataset.Name']]}
        clause = self.handler.gen_clauses(mquery, keylist)
        query = self.handler.build_query(clause, keylist)
        print query

    def test_single_query4(self):
        """test query with manually sqlalchemy select"""
        process_dataset = self.handler.find_table('ProcessedDataset')
        primary_dataset = self.handler.find_table('PrimaryDataset')
        # columns, whereclause=None, from_obj=None, distinct=False, having=None,
        # correlate=True, prefixes=None, **kwargs
        select_test = select(columns=[process_dataset.c.CreateDate,primary_dataset.c.Name])\
                        .correlate(primary_dataset.c.ID == process_dataset.c.PrimaryDataset)\
                        .where(primary_dataset.c.Name == 'test')
        keylist = {'keywords': ['dataset.createdate','primds'],
                   'constraints': ['primds.name'],
                   'keyset':['ProcessedDataset.CreateDate','PrimaryDataset.Name','PrimaryDataset.Name'],
                   'mkeywords':[['ProcessedDataset.CreateDate'],['PrimaryDataset.Name']]}
        query = self.handler.build_query(select_test, keylist)
        print query

class TestLive(unittest.TestCase):
    """live test """
    def setUp(self):
        """initialize test sqlite db then metadata"""
        if os.path.exists('unittest.db'):
            os.unlink('unittest.db')
        test_db = UnittestDB()
        self.metadata = test_db.load_with_fake_data('oracle.sql',
                            'sqlite:///unittest.db')
        self.handler = SchemaHandler(self.metadata.tables)
        self.mapper = Mapper()
        self.mapper.load_mapfile('map.yaml')
        self.mapper.validate_map(self.metadata.tables)
        self.handler._schema.recognize_type(self.mapper)
        self.handler._schema.handle_alias()
        self.handler._schema.gen_attr_links(self.mapper)
        simschema = self.handler._schema.gen_simschema()
        simschema.update_nodelist()
        graph = simschema.get_wgraph_from_schema()
        self.handler.subconstructors.append(ConstructQuery(graph, weighted=True))
        nodes = set(range(len(simschema.ordered)))
        self.handler.subnodes.append(nodes)
        self.handler._simschema = simschema



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
        process_dataset = self.handler.find_table('ProcessedDataset')
        data_tier = self.handler.find_table('DataTier')
        primary_dataset = self.handler.find_table('PrimaryDataset')
        files = self.handler.find_table('Files')

        # First try a regular select query.
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
              primary_dataset.c.CreatedBy]).where(process_dataset.c.ID == 0)
        print "regular select ", select_test
        results = select_test.execute()
        rows = results.fetchall()
        self.display_rows(rows)

        # Then use our software to modify one.
        keylist = {
            'keywords': ['dataset', 'tier','primds.createby'],
            'constraints':[],
            'keyset':['ProcessedDataset.Name','DataTier.Name','PrimaryDataset.CreatedBy'],
            'mkeywords':[['ProcessedDataset.Name'],['DataTier.Name'],['PrimaryDataset.CreatedBy']]
            }
        query = self.handler.build_query(None, keylist)
        print "modified select", query
        select_clause = query
        results = select_clause.execute()
        rows = results.fetchall()
        self.display_rows(rows)
        self.assertEqual(len(rows[0]), 3)

def suite():
    """suite all test together"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaHandler))
    suite.addTest(unittest.makeSuite(TestLive))
    return suite

if __name__ == '__main__':
#    import ConfigureLog
#    ConfigureLog.configurelog()
#    logging.basicConfig(stream=sys.stderr)
#    logging.getLogger("ConstructQuery").setLevel(logging.DEBUG)
    unittest.TextTestRunner(verbosity=2).run(suite())



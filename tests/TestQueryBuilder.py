#!/usr/bin/env python
"""
Test QueryBuilder on Schema object
"""

# system modules
import unittest
import os

from logging import getLogger
from StringIO import StringIO
from sqlalchemy import select

# local modules
from pyquerybuilder.qb.Schema import Schema, find_table, find_table_name
from pyquerybuilder.qb.Schema import make_view_without_table
from pyquerybuilder.qb.DotGraph import DotGraph
try:
    from UnittestDB import load_from_file, UnittestDB
except :
    pass
from pyquerybuilder.qb.WriteSqlAlchemyGraph import write_query_alchemy_graph
_LOGGER = getLogger("ConstructQuery")


class TestQueryBuilder(unittest.TestCase):
    """Test class for Querybuilder"""
    def setUp(self):
        """default"""
        pass

    def tearDown(self):
        """default """
        pass

    def test_yaml_graph(self):
        """test create schema from yaml
           make a dotgraph
           output via query_builder"""
        query_builder = Schema(load_from_file("starting_db.yaml").tables)
        dot = DotGraph(file("z.dot","w"))
        query_builder.write_graph(dot)

    def run_elements(self, query_builder, elements):
        """create query_builder via elements"""
        query = query_builder.build_query(elements)
        return str(query)

    def test_single_query(self):
        """test create schema from yaml
           get table by name
           create a select query on this table
           create a query builder and build this query"""
        metadata = load_from_file("starting_db.yaml")
        process_dataset = find_table(metadata, 'ProcessedDataset')
        select_test = select([process_dataset.c.Name],
                                process_dataset.c.ID == 0)
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print str(query)

    def test_yaml_query(self):
        """test yaml query, using multiple tables"""
        metadata = load_from_file("starting_db.yaml")
        process_dataset = find_table(metadata, 'ProcessedDataset')
        data_tier = find_table(metadata, 'DataTier')
        process_dataset = find_table(metadata, 'PrimaryDataset')
        files = find_table(metadata, 'Files')
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
                           process_dataset.c.Description])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print str(query)
        select_test1 = select([process_dataset.c.Name, data_tier.c.Name,
                           files.c.LogicalFileName])
        query = query_builder.build_query(select_test1)
#        print str(query)

    def test_oracle_query(self):
        """test oracle query
           create test oracle db
           get meta data
           create select query on multiple table
           create query builder and build querys
           output in graph"""
        _LOGGER.debug("test_oracle_query start")
        test_db = UnittestDB()
        metadata = test_db.read_from_oracle('oracle.sql')
        process_dataset = find_table(metadata, 'ProcessedDataset')
        app_exec = find_table(metadata, 'AppExecutable')
        select_test = select([process_dataset.c.Name,
                        app_exec.c.ExecutableName])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print str(query)
        person = find_table(metadata, 'Person')
        select_test = select([process_dataset.c.Name,
                         app_exec.c.ExecutableName, person.c.Name])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
        dot = DotGraph(file("testOracleQuery.dot", "w"))

        write_query_alchemy_graph(dot, query)
#        print str(query)
        _LOGGER.debug("test_oracle_query finish")


    def test_oracle_simple(self):
        """test oracle simple query"""
        _LOGGER.debug("test_oracle_simple start")
        test_db = UnittestDB()
        metadata = test_db.read_from_oracle('oracle.sql')
        process_dataset = find_table(metadata, 'ProcessedDataset')
#        app_exec = find_table(metadata, 'AppExecutable')
        person = find_table(metadata, 'Person')
        select_test = select([person.c.Name])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print query
        select_test = select([process_dataset.c.Name])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print str(query)
        _LOGGER.debug("test_oracle_simple finish")

    def test_operators(self):
        """test operators"""
        metadata = load_from_file("starting_db.yaml")
        process_dataset = find_table(metadata, 'ProcessedDataset')
        data_tier = find_table(metadata, 'DataTier')
        process_dataset = find_table(metadata, 'PrimaryDataset')
#        files = find_table(metadata,'Files')
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
                process_dataset.c.Description], process_dataset.c.ID==0)
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
#        print str(query)

    def test_dotgraph(self):
        """test DotGraph"""
        query_builder = Schema(load_from_file("starting_db.yaml").tables)
        output = StringIO()
        dot = DotGraph(output)
        query_builder.write_graph(dot)
#        print output.getvalue()

    def test_views(self):
        """test views """
        metadata = load_from_file("complex_db.yaml")
        person_name = find_table_name(metadata, 'Person')
        (view, _) = make_view_without_table(metadata,
                   person_name, 'FullName')
#        process_dataset = find_table(view, 'ProcessedDatasetView')
#        data_tier = find_table(view, 'DataTierView')
#        process_dataset = find_table(view, 'PrimaryDatasetView')
#        files = find_table(view, 'FilesView')

        # This shows what happens to the foreign keys
        #      when you make a select statement.
        for table_name in view.tables:
            table = view.tables[table_name]
            for f_key in table.foreign_keys:
                vals = {}
                vals['table'] = table_name
                vals['column'] = f_key.parent.name
                if f_key.parent.table.__dict__.has_key('name'):
                    vals['from'] = f_key.parent.table.name
                else:
                    vals['from'] = "none"
                if f_key.column.table.__dict__.has_key('name'):
                    vals['to'] = f_key.column.table
                else:
                    vals['to'] = "none"
                _LOGGER.debug(
                    "test_views %(table)s.%(column)s %(from)s->%(to)s"
                    % vals)

    def test_view_build(self):
        """test view build """
        _LOGGER.debug("test_view_build start")
        metadata = load_from_file("complex_db.yaml")
        person_name = find_table_name(metadata, 'Person')
        (view, foreign_keys) = make_view_without_table(metadata,
                                 person_name, 'FullName')
#        for table_name in view.tables:
#            print table_name, list(view.tables[table_name].c)
#        files = find_table(view, 'FilesView')
        process_dataset = find_table(view, 'ProcessedDatasetView')
        data_tier = find_table(view, 'DataTierView')
        process_dataset = find_table(view, 'PrimaryDatasetView')
        query_builder = Schema(view.tables, foreign_keys)
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
                             process_dataset.c.Description],
            process_dataset.c.ID==0)
        query = query_builder.build_query(select_test)
        _LOGGER.debug("test_view_build query: " + str(query))
        _LOGGER.debug("test_view_build finish")

class TestLive(unittest.TestCase):
    """live test """
    def setUp(self):
        """initialize test sqlite db then metadata"""
        if os.path.exists('unittest.db'):
            os.unlink('unittest.db')
        test_db = UnittestDB()
        self.metadata = test_db.load_with_fake_data('oracle.sql',
                            'sqlite:///unittest.db')

    def tearDown(self):
        """release resources"""
        self.metadata.bind.engine.dispose()
        os.unlink('unittest.db')

    def display_rows(self, rows):
        """display rows on LOGGER"""
        _LOGGER.debug(rows[0].keys())
        for row in rows:
            _LOGGER.debug(row)

    def test_read_query(self):
        """test read querys"""
        metadata = self.metadata
        process_dataset = find_table(metadata, 'ProcessedDataset')
        data_tier = find_table(metadata, 'DataTier')
        process_dataset = find_table(metadata, 'PrimaryDataset')
#        files = find_table(metadata, 'Files')

        # First try a regular select query.
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
              process_dataset.c.Description], process_dataset.c.ID == 0)
        results = select_test.execute()
#        rows = results.fetchall()
#        self.display_rows(rows)

        # Then use our software to modify one.
        select_test = select([process_dataset.c.Name, data_tier.c.Name,
                                 process_dataset.c.Description])
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
        _LOGGER.debug(query)
        select_clause = query
        results = select_clause.execute()
        rows = results.fetchall()
        self.display_rows(rows)
        self.assertEqual(len(rows[0]), 3)

        select_test = select([process_dataset.c.ID, process_dataset.c.Name,
                       data_tier.c.ID, process_dataset.c.Description],
                       process_dataset.c.ID == 0)
        query_builder = Schema(metadata.tables)
        query = query_builder.build_query(select_test)
        _LOGGER.debug(query)
        select_clause = query
        results = select_clause.execute()
        rows = results.fetchall()
        self.display_rows(rows)
        self.assertEqual(len(rows[0]), 4)

    def test_live_view(self):
        """ test live views"""
        _LOGGER.debug("test_live_view start")
        metadata = self.metadata
        person_name = find_table_name(metadata, 'Person')
        (view, foreignkeys) = make_view_without_table(metadata,
                              person_name, 'DistinguishedName')
#        for table_name in view.tables:
#            print table_name, list(view.tables[table_name].c)
        process_dataset = find_table(view, 'ProcessedDatasetView')
        app_exec = find_table(view, 'AppExecutableView')
        select_test = select([process_dataset.c.Name,
                              app_exec.c.ExecutableName])
        query_builder = Schema(view.tables, foreignkeys)
        query = query_builder.build_query(select_test)
        results = query.execute()
        rows = results.fetchall()
        _LOGGER.debug("test_live_view query: " + str(query))
        _LOGGER.debug("test_live_view result: %s" % (rows,))
        _LOGGER.debug("test_live_view finish")

def suite():
    """suite all test together"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryBuilder))
    suite.addTest(unittest.makeSuite(TestLive))
    return suite

if __name__ == '__main__':
#    import ConfigureLog
#    ConfigureLog.configurelog()
    unittest.TextTestRunner(verbosity=1).run(suite())



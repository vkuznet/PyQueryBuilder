#!/usr/bin/env python
"""
Test mapper object
"""
import unittest
from pyquerybuilder.tools.map_reader import Mapper
from UnittestDB import UnittestDB


class TestMapper(unittest.TestCase):
    """Test Mapper class"""
    def setUp(self):
        """ auto init"""
        self.mapper = Mapper()
        self.mapfile = 'testmap.yaml'
        udb = UnittestDB()
        metadata = udb.load_from_file('starting_db.yaml')
        self.mapper.load_mapfile(self.mapfile)
        self.mapper.validate_map(metadata.tables)
        self.assertEqual(22, len(self.mapper.dict))

    def test_get_key(self):
        """test get_key"""
        self.assertTrue('dataset.name' == self.mapper.get_key('Files.Path'))
        self.assertFalse('Dataset.name' == self.mapper.get_key('Files.Path'))
        self.assertFalse('dataset.name' == self.mapper.get_key('files.path'))

    def test_get_column(self):
        """test get_column"""
        self.assertTrue( \
          'ProcessedDataset.PhysicsGroup' == self.mapper.get_column('phygrp'))
        self.assertFalse( \
          'Block.Name' ==  self.mapper.get_column('Block'))
        self.assertFalse( \
          'FILES.Path' == self.mapper.get_column('dataset'))
        self.assertFalse( \
          'files.block' == self.mapper.get_column('file.block'))

    def test_get_table(self):
        """test get_table"""
        self.assertTrue( \
            'ProcessedDataset'.lower() ==  self.mapper.get_table('dataset'))

def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMapper))
    return suite

#
# main
#
if __name__ == "__main__":

    unittest.TextTestRunner(verbosity=2).run(suite())


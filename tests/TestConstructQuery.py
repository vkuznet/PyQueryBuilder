#!/usr/bin/env python
"""
Test ConstuctQuery object
"""

from pyquerybuilder.qb.ConstructQuery import ConstructQuery
#from TestGraph import TestGraph
import unittest

class TestConstructQuery(unittest.TestCase):
    """Test ContructQuery class"""
    def setUp(self):
        """ auto init"""
        pass

    def test_text_graph(self):
        """ test text graph"""
        pass
#        schema_string = """
#            ProcessedDataset:
#              - member : status
#              - member : group
#              - member   : PrimaryDataset
#                join     : PrimaryDataset
#            PrimaryDataset:
#              - Description, PrimaryDatasetDescription
#              - joinType, PrimaryDSType
#            """
         #schemaDict = yaml.load(schemaString)
         #print schemaDict

    def list_test(self, result, test):
        """ list test """
        res = list(result)
        res.sort()
        self.assertEqual(tuple(res), test)


    def test_small_graph(self):
        """test small graph generate from get_statment_joins """
        schema = (
            (1, 2), # 0->1,2
            (3, ),   # 1->3
            (),
            ()
            )
        construct_query = ConstructQuery(schema)
        (_, res0) = construct_query.get_statement_joins((0, 3))
        self.list_test(res0, ((1, 0), (3, 1)))
        (_, res1) = construct_query.get_statement_joins((3, 1, 0))
        self.list_test(res1, ((1, 0), (3, 1)))
        (_, res2) = construct_query.get_statement_joins((0, 2))
        self.list_test(res2, ((2, 0),))
        (_, res3) = construct_query.get_statement_joins((0, ))
        self.list_test(res3, ())

    def test_subtree(self):
        """test subtree generation from get_smallest_subtree"""
        schema = (
            (1, 2), # 0->1,2
            (3, ),   # 1->3
            (),
            ()
            )
        construct_query = ConstructQuery(schema)
        res = construct_query.get_smallest_subtree((0, 3))
#        print "subtree 0 3", res
        #self.assertEqual(res, RootedGraph())
        res = construct_query.get_smallest_subtree((3, 1, 0))
#        print "subtree 0 1 3", res
        #self.listTest(res, ((1,0), (3,1)))
        res = construct_query.get_smallest_subtree((0, 2))
#        print "subtree 0 2", res
        #self.listTest(res, ((2,0),))
        res = construct_query.get_smallest_subtree((0, ))
#        print "subtree 0", res

def suite():
    """test suite for all TestConstructQuery class"""
    suite = unittest.TestSuite()
#    suite.addTest(unittest.makeSuite(TestGraph))
    suite.addTest(unittest.makeSuite(TestConstructQuery))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 3).run(suite())


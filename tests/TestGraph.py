#!/usr/bin/env python
"""
Test Graph object 
"""

import unittest
from pyquerybuilder.qb.Graph import  Graph, RootedGraph

class TestGraph(unittest.TestCase):
    """unittest for Graph class"""
    def setUp(self):
        """two graph generated"""
        self.graph0 = (
            (1, 2), # 0->1,2
            (3, ),   # 1->3
            (),
            ()
            )
        self.graph1 = (
            (),
            (2, ),
            (),
            ()
            )
    def test_breadth_iterator(self):
        """test breadth first iterator and print edges"""
        test_graph = Graph(self.graph0)
#        for (node, parent) in test_graph.breadth_first(0):
#            print node, parent
        test_graph = RootedGraph(self.graph0, 0)
#        for (node, parent) in test_graph.breadth_first():
#            print node, parent

    def test_breadth_search(self):
        """test breadth first search, verify the path by known results """
        test_graph = Graph(self.graph0)
        span = test_graph.breadth_first_search(0)
#        print "span 2", span
        self.assertEqual(span, Graph(( (1, 2), (3, ), (), ())))
        span = test_graph.breadth_first_search(1)
#        print "span 1", span
        self.assertEqual(span, Graph((
            (), (3, ), (), ()
            )))
        span = test_graph.breadth_first_search(3)
#        print "span 3", span
        self.assertEqual(span, Graph((
            (), (), (), ()
            )))

    def test_coverage(self):
        """test coverage, verify the set by known results"""
        test_graph = Graph(self.graph0)
        cover = test_graph.get_coverage()
        self.assertEqual(cover, set((0, 1, 2, 3)))
        cover = Graph(self.graph1).get_coverage()
        self.assertEqual(cover, set((1, 2)))

    def test_undirect(self):
        """test generation of undirect Graph"""
        test_graph = Graph(self.graph1)
        test_result = test_graph.get_undirected()
        self.assertEqual(test_result, Graph(((), (2, ), (1, ), ())))
        test_graph = Graph(self.graph0)
        test_result = test_graph.get_undirected()
        self.assertEqual(test_result, Graph(((1, 2), (0, 3), (0, ), (1, ))))

    def test_subtree(self):
        """test RootedGraph function of subtree which don't
        contain nodes in the node_set"""
        test_graph = RootedGraph(self.graph0, 0)
        test_subtree = test_graph.subtree_including(set((0, )))
        self.assertEqual(test_subtree, RootedGraph(((), (), (), ()), 0))
        test_subtree = test_graph.subtree_including(set((0, 1)))
        self.assertEqual(test_subtree, RootedGraph(((1, ), (), (), ()), 0))
        test_subtree = test_graph.subtree_including(set((2, )))
        self.assertEqual(test_subtree, RootedGraph(((2, ), (), (), ()), 0))
        test_subtree = test_graph.subtree_including(set((0, 2, 3)))
        self.assertEqual(test_subtree, RootedGraph(((1, 2), (3, ), (), ()), 0))

    def test_reverse(self):
        """test reverse function"""
        test_graph = Graph(self.graph0)
        test_result = test_graph.get_reverse()
#        print test_result
        self.assertEqual(test_result, Graph(((), (0, ), (0, ), (1, ))))

    def test_edges_from_nodes(self):
        """test get edges from nodes"""
        test_graph = Graph(self.graph0)
        test_result = test_graph.edges_from_node(0)
#        print test_result
        self.assertEqual(test_result, set(((0, 1), (1, 3))))
        test_result = test_graph.edges_from_node(1)
#        print test_result
        self.assertEqual(test_result, set(((1, 3), )))

def suite():
    """generate suite for all unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGraph))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite())


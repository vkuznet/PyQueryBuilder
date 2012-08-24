#!/usr/bin/env python
"""
Test OriginSchema and TSchema
"""

from pyquerybuilder.qb.NewSchema import OriginSchema, TSchema
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.Graph import Graph
from pyquerybuilder.qb.SchemaHandler import SchemaHandler
from pyquerybuilder.tools.map_reader import Mapper
try:
    from UnittestDB import load_from_file, UnittestDB
except :
    pass


from logging import getLogger

import unittest

class TestOriginSchema(unittest.TestCase):
    """Test OriginSchema"""
    def setUp(self):
        """auto init"""
        metadata = load_from_file("starting_db.yaml")
        self.oschema = OriginSchema(metadata.tables)
        self.mapper = Mapper()
        self.mapper.load_mapfile('testmap.yaml')
        self.mapper.validate_map(metadata.tables)
        self.oschema.check_connective()

    def test_yaml_graph(self):
        """test create schema from yaml
           make a dotgraph
           output via query_builder"""
        oschema = self.oschema
        dot = DotGraph(file("z.dot","w"))
        oschema.write_graph(dot)
        self.assertTrue(12 == len(oschema.nodelist))

#    def test_check_connective(self):
#        """test check connectives """
#        self.oschema.check_connective()

    def test_recognize_type(self):
        """test recognize three type kinds of nodes"""
        oschema = self.oschema
        oschema.recognize_type(self.mapper)
#        for node in oschema.nodelist:
#            print oschema.nodelist[node],oschema.nodelist[node].parent
#        print oschema.v_ent
#        print oschema.v_rel
#        print oschema.v_attr
        self.assertTrue(6 == len(oschema.v_ent))
        self.assertTrue(1 == len(oschema.v_rel))
        self.assertTrue(3 ==  len(oschema.v_attr))

    def test_handle_alias(self):
        """test handle alias"""
        oschema = self.oschema
        oschema.recognize_type(self.mapper)
        oschema.handle_alias()
        self.assertTrue(4 == len(oschema.v_attr))

    def test_gen_attr_link(self):
        """test attribute link generation"""
        self.oschema.recognize_type(self.mapper)
        attr_path, _ = self.oschema.gen_attr_links(self.mapper)
        self.assertEqual('Files.Dataset_ProcessedDataset.ID'.lower(), \
            attr_path['dataset.name'][0].name.lower())

    def test_gen_simschema(self):
        """test generate simschema"""
        oschema = self.oschema
        oschema.recognize_type(self.mapper)
        oschema.handle_alias()
        attr_path, _ = oschema.gen_attr_links(self.mapper)
        simschemas = oschema.gen_simschema()
        for simschema in simschemas:
            simschema.update_nodelist()
        self.assertEqual(1, len(simschemas))

class TestTSchema(unittest.TestCase):
    """Test TSchema"""
    def setUp(self):
        metadata = load_from_file("starting_db.yaml")
        oschema = OriginSchema(metadata.tables)
        oschema.check_connective()
        self.mapper = Mapper()
        self.mapper.load_mapfile('testmap.yaml')
        self.mapper.validate_map(metadata.tables)
        oschema.recognize_type(self.mapper)
        oschema.handle_alias()
        attr_path, _ = oschema.gen_attr_links(self.mapper)
        self.simschemas = oschema.gen_simschema()
        for simschema in self.simschemas:
            simschema.update_nodelist()

    def test_get_wgraph_from_schema(self):
        """test get wgraph from schema"""
        graph1 = [[(5, 0), (4, 0)], [(4, 0)], [], [(4, 0)], [(2, 0)], [(4, 0)]]
        graph2 = self.simschemas[0].get_wgraph_from_schema()
        self.assertEqual(len(graph1), len(graph2))
        for idx in range(len(graph1)):
            self.assertEqual(graph1[idx].sort(), graph2[idx].sort())

    def test_get_graph_from_schema(self):
        """test get graph from schema"""
        graph1 = [[5, 4], [4], [], [4], [2], [4]]
        graph2 = self.simschemas[0].get_graph_from_schema()
        self.assertEqual(len(graph1), len(graph2))
        for idx in range(len(graph1)):
            self.assertEqual(graph1[idx].sort(), graph2[idx].sort())

    def test_write_graph(self):
        """test write graph"""
        dot = DotGraph(file("z.dot","w"))
        self.simschemas[0].write_graph(dot)

    def test_get_cycle_basis(self):
        """test get basic cycles"""
        simschema = self.simschemas[0]
        relations = simschema.get_graph_from_schema()
        graph = Graph(relations)
        ugraph = graph.get_undirected()
        cycles2 = simschema.get_cycle_basis(ugraph._graph)
        cycles2 = cycles2[0]
        cycles = ['Files', 'ProcessedDataset', 'Block']
        cycles1 = [\
        simschema.ordered.index(simschema.nodelist[node.lower()]) for node in cycles]
        cycles1.sort()
        cycles2.sort()
        self.assertEqual(len(cycles1), len(cycles2))
        for idx in range(len(cycles1)):
            self.assertEqual(cycles1[idx], cycles2[idx])

    def test_write_cyclic_graph(self):
        """test write cyclic graph"""
        dot = DotGraph(file("z.dot","w"))
        self.simschemas[0].write_cyclic_graph(dot, "basic_cycles")

    def test_gen_subgraph(self):
        """test generating subgraph"""
        pass

def suite():
    """suite all test together"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOriginSchema))
    suite.addTest(unittest.makeSuite(TestTSchema))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

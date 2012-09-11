#!/usr/bin/env python
"""
Given a graph representing a schema and nodes to hit, this class does a poor
man's travelling salesman solution.
"""
__author__ = "<liangd@ihep.ac.cn>; <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

# system modules
from logging import getLogger

# local modules
from pyquerybuilder.qb.DotGraph import DotGraph
from pyquerybuilder.qb.Graph import Graph
from pyquerybuilder.qb.WGraph import WGraph
from pyquerybuilder.qb.WGraph import RootedWGraph
from pyquerybuilder.qb.CalMCST import calmcst
from pyquerybuilder.qb.Prim import prim
from pyquerybuilder.qb.Steiner import steiner

_LOGGER = getLogger("ConstructQuery")


class ConstructQuery(object):
    """Given a graph representing a schema and nodes to hit, this class does
    a poor man's travelling salesman solution."""
    def __init__(self, connectivity, weighted=False):
        """Connectivity describes which tables have foreign keys
        into which other tables."""
        if weighted:
            graph = WGraph(connectivity)
        else:
            graph = Graph(connectivity)
        self.graph = graph
        self._mst = [[]] * len(self.graph)
        self.undirected_graph = graph.get_undirected()
        self._spanning = []
        self.weighted = weighted
        # traversing graph
        #    get spanning path of BFS from this node
        #    self._spannning stores those path
        for node_index in range(0, len(self.undirected_graph)):
            span = self.undirected_graph.breadth_first_search(node_index)
            self._spanning.append(span)
        if weighted:
            for index in range(0, len(self.graph)):
                mst = prim(graph._graph, range(len(self.graph)), index)
                self._mst[index] = RootedWGraph(mst, index)
                self.undirected_graph.gen_dist_matrix()

    def print_spans(self):
        """print every spans in this spanning collection"""
        span_index = 0
        for span in self._spanning:
            dot = DotGraph(file("span%d.dot" % (span_index),"w"))
            span.write_graph(dot)
            span_index = span_index+1

    def get_smallest_subtree(self, query_elements):
        '''Find the subtree containing the query elements.'''
        query_set = set(query_elements)
        min_len = len(self._spanning) + 1
        smallest_span = None
        span_index = 0
        for span in self._spanning:
            sub_span = span.subtree_including(query_set)
            if sub_span is not None:
                if sub_span.get_edges_number() < min_len:
                    min_len = sub_span.get_edges_number()
                    smallest_span = sub_span
            span_index = span_index + 1

        return smallest_span

    def get_leastw_subtree(self, query_elements):
        '''Find the subtree containing the query elements.'''
        if not self.weighted:
            return self.get_smallest_subtree(query_elements)
        query_set = set(query_elements)
        min_len = len(self._spanning) + 1
        smallest_span = None
        span_index = 0
        for span in self._spanning:
            sub_span = span.subtree_including(query_set)
            if sub_span is not None:
                if sub_span.get_edges_weight() < min_len:
                    min_len = sub_span.get_edges_weight()
                    smallest_span = sub_span
            span_index = span_index + 1

        return smallest_span


    def get_statement_joins(self, query_elements):
        '''
        The argument is a list of which tables contain the desired elements.
        The return value is a list of joins between those tables.
        '''
        query_set = set(query_elements)

        edge_sets = []
        min_len = len(self._spanning)
        min_index = -1
        for node_index in range(0, len(self._spanning)):
            subs = self._spanning[node_index].get_edges_including(query_set)
            if len(subs) < min_len:
                min_len = len(subs)
                min_index = node_index
            edge_sets.append(subs)
        return (min_index, edge_sets[min_index])

    def get_mcst(self, query_elements, lefts):
        """
        Iterator approach of calculating mcst
        """
        _LOGGER.debug('query_elements %s' % str(query_elements))
        _LOGGER.debug('graph %s' % str(self.undirected_graph._graph))
        _LOGGER.debug('lefts %s' % str(lefts))
        wt, subtree = calmcst(query_elements, self.undirected_graph._graph)
        root = subtree.root_index
        if root in lefts:
            _LOGGER.debug("swith_root")
            subtree.switch_root(lefts)
        sub_span = self._mst[subtree.root_index]\
                .subtree_including(subtree.nodesets())
        if sub_span != None and sub_span.sum_weight() < wt:
            return sub_span
        else:
            return subtree

    def get_steiner(self, query_elements, lefts):
        """
        dynamic programming for steiner tree problem
        """
        subpaths, root = steiner(self.undirected_graph._graph, query_elements, \
                self.undirected_graph.d, \
                self.undirected_graph.PT)
        n = len(self.undirected_graph._graph)
        subtree = [[]] * n
        for i, j in subpaths:
            subtree[i].append((j, 0))
            subtree[j].append((i, 0))
        subtree = RootedWGraph(subtree, root)
        root = subtree.root_index
        if root in lefts:
            _LOGGER.debug("swith_root")
            subtree.switch_root(lefts)
        return subtree

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
from pyquerybuilder.qb.WGraph import UWGraph
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
        glen = len(self.graph)
        self._mst = [[]] * glen
        self.undirected_graph = graph.get_undirected()
        self._spanning = []
        self.weighted = weighted
        # traversing graph
        #    get spanning path of BFS from this node
        #    self._spannning stores those path
        for node_index in range(0, glen):
            span = self.undirected_graph.breadth_first_search(node_index)
            self._spanning.append(span)
        if weighted:
            for index in range(0, glen):
                mst = prim(self.undirected_graph._graph, range(glen), index)
                self._mst[index] = UWGraph(mst, index)
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
            sub_span2 = self._mst[span_index].subtree_including(set(query_elements))
            if sub_span is not None:
                if sub_span.get_edges_weight() < min_len:
                    min_len = sub_span.get_edges_weight()
                    smallest_span = sub_span
                if sub_span2.sum_weight() < min_len:
                    min_len = sub_span2.sum_weight()
                    smallest_span = sub_span2
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
        fsub = None
        fwt = 65536
        for subtree, wt in calmcst(query_elements, self.undirected_graph._graph):
            if wt < fwt:
                fwt = wt
                fsub = subtree
            else:
                continue
            ##print "reviewing"
            ##print subtree, wt
            root = subtree.root_index
            if root in lefts:
                _LOGGER.debug("swith_root")
                ##print "switch_root"
                subtree.switch_root(lefts)
            ##print "NODESETS", subtree.nodesets()
            sub_span = self._mst[subtree.root_index]\
                    .subtree_including(set(query_elements))
                    #.subtree_including(subtree.nodesets())
            ##print sub_span, "sub_span"
            ##print "sub_span_sum", sub_span.sum_weight()
            if sub_span != None and sub_span.sum_weight() <= fwt:
                #print sub_span, "sub_span"
                fsub = sub_span
                fwt = sub_span.sum_weight()
            root = sub_span.root_index
            subt = self._spanning[root].subtree_including(set(query_elements))
            if subt.get_edges_weight() <= fwt:
                fsub = subt
                fwt = subt.get_edges_weight()
        ##print fsub,"subtree ", fwt, "fwt"
        ##print "end looking"
        return fsub

    def get_steiner(self, query_elements, lefts):
        """
        dynamic programming for steiner tree problem
        """
        subpaths, root = steiner(self.undirected_graph._graph, query_elements, \
                self.undirected_graph.d, \
                self.undirected_graph.PT)
        n = len(self.undirected_graph._graph)
        lk_set = set([])
        for lk in subpaths:
            ll, rr = lk
            lk_set.add(lk)
            if (rr, ll) in lk_set:
                lk_set.remove(lk)
        sub_span = [[] for _ in self.undirected_graph._graph ]
        for i, j in lk_set:
            sub_span[i].append((j, 0))
            sub_span[j].append((i, 0))
        subtree = RootedWGraph(sub_span, root)
        root = subtree.root_index
        if root in lefts:
            _LOGGER.debug("swith_root")
            subtree.switch_root(lefts)
        return subtree

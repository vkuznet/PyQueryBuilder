#!/usr/bin/env python
"""
This represents a directed graph.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

from logging import getLogger
_LOGGER = getLogger("ConstructQuery")

class Graph(object):
    """This represents a directed graph."""
    def __init__(self, graph):
        """The graph is a tuple, where each tuple memeber represents a node and
        the node contains a list of the other nodes to which it points. For
        instance, ((1,2),(3,),(),()) means node () points to node 1 and 2, node
        1 points to 3, and nodes 3 and 4 have no edges leaving them"""
        self._graph = tuple([tuple(x) for x in graph])
        self._coverage = None
        self._reverse  = None
        self._edge_count  = None

    def __eq__(self, other):
        """Compare each node are equal or not, Order of the edges doesn't counta
        when measuring equality."""
        if len(self._graph) is not other.__len__():
            return False
        equal = True
        for node_index in range(0, len(self._graph)):
            left = list(self._graph[node_index])
            right = list(other.get_adjacent(node_index))
            left.sort()
            right.sort()
            if left != right:
                equal = False
        return equal

    def __repr__(self):
        """overite to graph tuple"""
        return repr(self._graph)

    def __len__(self):
        """ovewrite to graph tuple"""
        return len(self._graph)

    def get_adjacent(self, node_index):
        """get adjacent of given node"""
        return self._graph[node_index]

    def get_edges_number(self):
        """return the number of edges"""
        if not self._edge_count:
            self._edge_count = reduce( lambda x, y: x+len(y), self._graph, 0 )
        return self._edge_count

    def get_nodes_number(self):
        """return the number of nodes"""
        # visited = [False for x in self._graph]
        visited = [False] * self.__len__()
        for node_index in xrange(0, len(self._graph)):
            node_points = self._graph[node_index]
            if node_points:
                visited[node_index] = True
                for node_point in node_points:
                    visited[node_point] = True
        return len(filter(lambda x: x is True, visited))

    def breadth_first_search(self, node_index):
        """Find a breadth first spanning tree of the graph. The return value
        is another graph."""
        unexplored = [node_index]
        #visited    = [False for x in self._graph]
        visited = [False] * self.__len__()
        span       = [[]    for x in self._graph]
        #span = [[]] * self.__len__()

        starting_node_index = node_index
        while unexplored:
            node_index = unexplored[0]
            if node_index >= len(visited) or node_index < 0:
                _LOGGER.debug("graph %s node_index %d start %d" %
                 (repr(self._graph), node_index, starting_node_index))
            visited[node_index] = True

            for adjacent in self._graph[node_index]:
                if not visited[adjacent]:
                    unexplored.append(adjacent)
                    visited[adjacent] = True
                    span[node_index].append(adjacent)

            del unexplored[0]
        return RootedGraph(span, starting_node_index)


    def breadth_first(self, node_index):
        """Return an iterator whose value is (child,parent) for every edge in
        the graph. it's in breadth first order"""
        unexplored = [(node_index, None)]
        #visited    = [False for x in self._graph]
        visited = [False] * self.__len__()
        #starting_node_index = node_index
        ( yield unexplored[0] )
        while unexplored:
            (node_index, _) = unexplored[0]
            visited[node_index] = True

            for adjacent in self._graph[node_index]:
                if not visited[adjacent]:
                    unexplored.append((adjacent, node_index))
                    visited[adjacent] = True
                    ( yield (adjacent, node_index) )

            del unexplored[0]
        return

    def get_edges_including(self, node_set):
        """Assumes we are working with a spanning tree with single directed
        edges. Finds edges including the node_set."""
        reverse = self.get_reverse()
        edges = set()
        for node in node_set:
            node_edges = reverse.edges_from_node(node)
            edges = edges.union(node_edges)
        return edges

    def get_undirected(self):
        """get the undirected Graph based on the directed Graph"""
        undirected = [set(edges) for edges in self._graph]
        for node_index in range(0, len(undirected)):
            for edge_end in undirected[node_index]:
                undirected[edge_end].add(node_index)
        return Graph((tuple(x) for x in undirected))

    def get_coverage(self):
        """Coverage returns the set of nodes in the graph.
        We say a node is in the graph if it is on an edge."""
        if self._coverage:
            return self._coverage
        self._coverage = set()
        for node_index in range(0, len(self._graph)):
            node = self._graph[node_index]
            if node:
                self._coverage.add(node_index)
                for end_index in node:
                    self._coverage.add(end_index)
        return self._coverage

    def get_reverse(self):
        """Reverse the direction of the graph."""
        if self._reverse:
            return self._reverse

        trackback = [set() for x in self._graph]
        #trackback = [set()] * self.__len__()
        for node_index in range(0, len(self._graph)):
            for edge in self._graph[node_index]:
                trackback[edge].add(node_index)
        self._reverse = Graph(trackback)
        return self._reverse

    def edges_from_node(self, node_index):
        """Given a node, follow its edges until the end. Return the edges.
        Assumes only one edge out of each node. breadth first,
        (node,next_node)"""
        edges = set()
        next_nodes = self._graph[node_index]
        while next_nodes:
            next_node = next_nodes[0]
            edges.add((node_index, next_node))
            node_index = next_node
            next_nodes = self._graph[node_index]
        return edges

    def write_graph(self, dot):
        """create a DotGraph by addin all the edges from graph,
        then do the output"""
        dot.set_name("G")
        for start_index in range(0, len(self._graph)):
            end = self._graph[start_index]
            for end_index in end:
                dot.add_edge(repr(start_index), repr(end_index))
        dot.finish_output()

    def get_subgraph(self, node_list):
        """clear out the unused edge"""
        graph = []
        for node_index in range(len(self._graph)):
            if node_index not in node_list:
                graph.append([])
                continue
            newnode = []
            node = self._graph[node_index]
            for end_node in node:
                if end_node in node_list:
                    newnode.append(end_node)
            graph.append(newnode)
#        print "==========rem unsused edge afte split union external ========"
#        print graph
#        print "======end remove from split union external============"
        return Graph((tuple(x) for x in graph))

    def get_extendgraph(self, node_list):
        """clear out the unused edge"""
        graph = []
        for node_index in range(len(self._graph)):
            if node_index not in node_list:
                graph.append([])
                continue
            newnode = []
            node = self._graph[node_index]
            graph.append(node)
#        print "==========extend graph============"
#        print graph
#        print "======end extend graph============"
        return Graph((tuple(x) for x in graph))



    def detect_connection(self, root):
        """dfs approach to find the branch of a graph"""
        ugraph = self.get_undirected()._graph
        visited = set([])
        queue = [root]

        while queue:
            top = queue.pop()
            visited.add(top)
            for node in ugraph[top]:
                if node not in visited:
                    queue.insert(0, node)
                    visited.add(node)
#        print "========get the spanning tree from root=============="
#        print ugraph
#        print root
#        print visited
#        print "========end of geting spanning tree from root=============="
        return self.get_extendgraph(visited)

    def get_inlinks(self, snode):
        """get the inlinks to a node"""
        inlinks = []
        for index in range(len(self._graph)):
            for node in self._graph[index]:
                if node == snode:
                    inlinks.append(index)
        return inlinks

    def get_expanding(self, node_list, excludes):
        """get expanding graph, following the direction of the edges"""
#        print excludes
        visited = set([])
        queue = node_list[:]
        graph = [ [] for x in range(len(self._graph)) ]

        while queue:
            top = queue[0]
            queue.remove(top)
            visited.add(top)
            for node in self._graph[top]:
                if node in excludes:
                    continue
                if node in visited:
                    if top in node_list or node in node_list:
                        graph[top].append(node)
                    continue
                graph[top].append(node)
                if queue.count(node) == 0:
                    queue.append(node)

        for node in node_list:
            for innode in self.get_inlinks(node):
                if innode not in excludes:
                    queue.append(innode)
#        print "inlinks"
#        print queue
        while queue:
            top = queue[0]
            queue.remove(top)
            if top in visited:
                continue
            visited.add(top)
            for node in self._graph[top]:
                graph[top].append(node)
                if queue.count(node) == 0:
                    queue.append(node)

        return Graph((tuple(x) for x in graph))


class RootedGraph(Graph):
    """a graph generated from (nodes, root_node)"""
    def __init__(self, graph, root, *args):
        """initialize via invoke parent's init"""
        apply(Graph.__init__, (self, graph) + args)
        self.root_index = root

    def __repr__(self):
        """ovewrite"""
        return "Root(%d) %s" % (self.root_index, Graph.__repr__(self))

    def add_branch_in_set(self, node_index, node_set, add_to, visited):
        """given a node set, fill the available edges on that"""
        branches = self._graph[node_index]
        add = []
        visited.append(node_index)
        if branches:
            for branch in branches:
                if branch in visited:
                    continue
                if self.add_branch_in_set(branch, node_set, add_to, visited):
                    add.append(branch)

        add_to[node_index] = add
        if add or (node_index in node_set):
            return True
        return False

    def breadth_first(self):
        """calling Graph's meathod"""
        return apply(Graph.breadth_first, (self, self.root_index))

    def subtree_including(self, node_set):
        """Find a subtree of a directed, acyclic graph pruning
        branches which don't contain nodes in the node_set.
        return subtree from node_set"""
        if not node_set.issubset(self.get_coverage()):
            return None

        #add_to = [[] for x in self._graph]
        add_to = [[]] * self.__len__()
        visited = []
        self.add_branch_in_set(self.root_index, node_set, add_to, visited)
        subtree = RootedGraph(add_to, self.root_index)
        del visited
        return subtree


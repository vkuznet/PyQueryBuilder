#!/usr/bin/env python

"""
This class reads sqlalchemy schema metadata in order to construct
joins for an arbitrary query.

Review all the foreign key links.
"""

__author__ = "Dong Liang <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.11 $"

# system modules
from logging import getLogger

from sqlalchemy.schema import ForeignKeyConstraint
from pyquerybuilder.qb.Node import Node, find, make_set, union
from pyquerybuilder.qb.LinkObj import CLinkObj, LinkObj
from pyquerybuilder.qb.Graph import Graph
from pyquerybuilder.qb.WGraph import WGraph
from pyquerybuilder.qb.DotGraph import MultiDot
from pyquerybuilder.qb.ConstructQuery import ConstructQuery
from pyquerybuilder.utils.Utils import similar

from pprint import pprint
#from pyquerybuilder.tools.map_reader import Mapper
#from sqlalchemy.sql.expression import Select

_LOGGER = getLogger("ConstructQuery")

class TSchema(object):
    """
    class encapsulate sub-schema which directly map to a subgraph.
    By means of answering a query, a sub-schema handle build query request:
    Input: sqlalchemy query without FROM clause.
    Output: sqlalchemy query with From clause.
    """
    def __init__(self, nodelist, links, owner = None):
        """
        Tables are ordered, thereby there is an index for each table.
        Adjacent link are used to construct a graph, by tables adjacent
        link could be rebuild easily.
        How to represent multiple link between tables.
        """
        self.nodelist = nodelist # dictionary of Node
        self.links = links # dictionary of CLinkObj
        self.ordered = [] # ordered of Nodes
        for node in self.nodelist.values():
            self.ordered.append(node)

    def print_schema(self):
        """Print schema dict"""
        banner = "-----------------%s %d--------------"
        print banner % ("links", len(self.links))
        pprint(self.links)
        print banner % ("tables", len(self.nodelist))
        pprint(self.nodelist)

    def update_nodelist(self):
        """update outlinks in each node by review links"""
        templist = []
        for node in self.nodelist.values():
            for link in node.outlinks:
                if link not in self.links:
                    templist.append(link)
            for link in templist:
                node.outlinks.pop(link)
            templist = []

    def cal_order(self):
        """recalculate the order for table"""
        ordered = []
        for node in self.nodelist.values():
            ordered.append(node)
        ordered.sort()
        self.ordered = ordered

    def get_graph_from_schema(self):
        """
        Build graph with node and links
        ((1,2),(3),(4,5), ...) a graph is represented as adjacent list
        """
        if not self.ordered:
            self.cal_order()
        relations = []
        ordered = self.ordered
        for index in range(0, len(ordered)):
            relations.append([])
        for index in range(0, len(ordered)):
            for link in ordered[index].outlinks.values():
                pos = ordered.index(self.nodelist[link.rtable])
                if not relations[index].count(pos):
                    relations[index].append(pos)
        return relations

    def get_wgraph_from_schema(self):
        """
        Build weighted graph with node and links
        (  ((1, 0.5),(2, 0.3)), ((3,0.6), ), (), (), ...)
        a graph is represented as adjacent list
        and weight is from link.weight
        """
        if not self.ordered:
            self.cal_order()
        relations = []
        ordered = self.ordered
        for index in range(0, len(ordered)):
            relations.append([])
        for index in range(0, len(ordered)):
            for link in ordered[index].outlinks.values():
                pos = ordered.index(self.nodelist[link.rtable])
                if not relations[index].count((pos, link.weight)):
                    relations[index].append((pos, link.weight))
        return relations

    def write_graph(self, dot, name="A"):
        """
        output dot graph for this schema, with table name as nodename
        """
        relations = self.get_graph_from_schema()
        order = self.ordered
        dot.set_name(name)
        for index in range(len(relations)):
            start_node = relations[index]
            for end_index in start_node:
                dot.add_edge(order[index], order[end_index])
        dot.finish_output()

    def write_cyclic_graph(self, bdot, name="C"):
        """
        output dot graph with core cyclic component
        """
        basename = name
        multidot = MultiDot(basename)
        relations = self.get_graph_from_schema()
        graph = Graph(relations)
        ugraph = graph.get_undirected()
        cycles = self.get_cycle_basis(ugraph._graph)
        nodes = None
        order = self.ordered
        for cycle in cycles:
#            print "--------------cycle----------"
#            print [order[node] for node in cycle]
            nodes = cycle
            dot = multidot.get_dot()
            for node in nodes:
                start_node = relations[node]
                for end_node in start_node:
                    if end_node in nodes:
                        dot.add_edge(order[node], order[end_node])
            dot.finish_output()

        nodes = set([])
        for cycle in cycles:
            nodes = nodes.union(set(cycle))
        for node in nodes:
            start_node = relations[node]
            for end_node in start_node:
                if end_node in nodes:
                    bdot.add_edge(order[node], order[end_node])
        bdot.finish_output()

    def get_cycle_basis(self, graph):
        """
        return a list of cycles which is the base of the cycles of
        graph

        referencing:
            An Algorithm for Finding a Fundamental Set of Cycles of a Graph
        by KEITH PATON
        """
        nodes = {}
        for index in range(len(graph)):
            nodes[index] = graph[index][:]
        gnodes = set(nodes)
        cycles = []
        root = None
        while gnodes: # go over all component
            if root == None:
                root = gnodes.pop()
            stack = [root]
            pred = {root:root} # previous node
            used = {root:set()} # visisted from root
            while stack:
                znd = stack.pop()
                zused = used[znd]
                for notbrowsed in nodes[znd]:# all node from znd
                    if notbrowsed not in used: # new node
                        pred[notbrowsed] = znd # znd find this node
                        stack.append(notbrowsed) # explore after znd
                        used[notbrowsed] = set([znd]) # root znd visited it
                    elif notbrowsed == znd: # self loop
                        cycles.append([znd])
                    elif notbrowsed not in zused: # found a cycle
                        parentnode = used[notbrowsed]
                        cycle = [notbrowsed, znd]
                        parent = pred[znd]
                        while parent not in parentnode:
                            cycle.append(parent)
                            parent = pred[parent]
                        cycle.append(parent)
                        cycles.append(cycle)
                        used[notbrowsed].add(znd)
            gnodes -= set(pred)
            root = None

#        print len(cycles), "was generated"
        return cycles

    def gen_subgraph(self, splition):
        """
        split this schema into sub graphs
            1. nodes not in splition can be attached freely
            2. first generate sub schema, and then generate sub graph
            3. sub graphs will extend as fk links direction
            4. sub graphs should be kept in sequence
        """
        core_node = set([])
        in_splition = []
        for split in splition:
            newsplit = []
            for node in split:
                if node not in self.nodelist.keys():
                    raise Exception("Wrong table inserted %s" % node)
                try:
                    core_node.add(self.ordered.index(self.nodelist[node]))
                except:
                    raise Exception("%d or %s is not a real table" % \
                        (len(self.ordered), node))
                newsplit.append(self.ordered.index(self.nodelist[node]))
            in_splition.append(newsplit)
#        full_node = set(range(len(self.ordered)))

#        external_node = full_node.difference(core_node)

        #subschema_list = []
        sub_nodelist = []
        #sub_link = []


        relations = self.get_wgraph_from_schema()
        graph = WGraph(relations)
        graph_list = []
#        self.print_graph(graph._graph)
#        print "===============external node=================="
#        print external_node
#        print "========end of external node=================="
        split = in_splition[0]
#        root = split[0]
#        print "===============split from user=================="
#        print split
        current_left = core_node.difference(set(split))
        subgraph = graph.get_expanding(split, current_left)
        #split = set(split).union(external_node)
        #print split
#        print "========end of split from user=================="
        #subgraph = graph.get_subgraph(split)
#        print subgraph
            # remove the edges out of the split++external
        #subgraph = subgraph.detect_connection(root)
            # the subgraph might be divided in several pieces
            # pick the one we needed
        subnodes = set([])
        for idx in range(len(subgraph._graph)):
            if subgraph._graph[idx] != ():
                subnodes.add(idx)
                for nod in subgraph._graph[idx]:
                    subnodes.add(nod[0])
        sub_nodelist.append(subnodes)
        graph_list.append(subgraph)
#            subgraph = subgraph.get_undirected().breadth_first(root)
        current_left = core_node.difference(set(split))
        for split in in_splition[1:]:
            # two operation might be seprated:
            #   1. get extension
            #   2. generate nodelist and links
#            root = split[0]
#            print "===============split from user=================="
#            print split
#            print "========end of split from user=================="
            current_left = current_left.difference(set(split))
            subgraph = graph.get_expanding(split, current_left)
            # remove the edges out of the split++external
            # the subgraph might be divided in several pieces
            # pick the one we needed
            subnodes = set([])
            for idx in range(len(subgraph._graph)):
                if subgraph._graph[idx] != ():
                    subnodes.add(idx)
                    for nod in subgraph._graph[idx]:
                        subnodes.add(nod[0])
            sub_nodelist.append(subnodes)
            graph_list.append(subgraph)
#            subgraph = subgraph.get_undirected().breadth_first(root)
#        multidot = MultiDot("subs")
#        for graph in graph_list:
#            nodes = graph._graph
#            dot = multidot.get_dot()
#            for index in range(len(nodes)):
#                start_node = nodes[index]
#                for end_node in start_node:
#                    dot.add_edge(order[index], order[end_node])
#            dot.finish_output()
        return graph_list, sub_nodelist

    def print_graph(self, graph):
        """Print graph"""
        for index in range(len(graph)):
            print "%d, %s" % (index, self.ordered[index])
            for node in graph[index]:
                print "-----%d, %s" % (node, self.ordered[node])



class OriginSchema(TSchema):
    """
    class encapsulate origin schema
        this schema might not fully connective, which means the
        corresponding graph might be splitted into pieces.
    """
    def __init__(self, tables, alias_table = None):
        """initialize tables with ent_node and rel_node"""
        TSchema.__init__(self, {}, {})
        self.tables = tables
        self.links = {}
        self.alias_table = {}
        self.atables = {} # SQLAlchemy need unique alias
        for table in self.tables.values():
            for cons in table.constraints:
                if isinstance(cons, ForeignKeyConstraint):
                    if cons.name == None:
                        cons.name = self.name_link(cons)
                    self.links[cons.name] = CLinkObj(cons.elements, cons.name)
        if alias_table:
            self.alias_table = alias_table
        self.nodelist = self.gen_nodelist() #sets for node division

        self.v_ent = set()
        self.v_attr = set()
        self.v_rel = set()

        self.e_rel = set()
        self.e_attr = set()

        self.ordered = []

    def gen_nodelist(self):
        """gen Node list"""
        node_dict = {}
        for table_name, table in self.tables.items():
            cons = self.get_links(table)
            node_dict[table_name] = Node(table_name, cons)
            make_set(node_dict[table_name])
        for fkey in self.links.values():
            union(node_dict[fkey.ltable], node_dict[fkey.rtable])

        return node_dict

    def recognize_type(self, mapper):
        """
        recognize three kinds of node type:
        entity node
        relationship node
        attribute node
        recognize two kinds of link type:
        relationship link
        attribute link
        """
        tablenames = set(self.tables.keys())
        k_table = set()
        if not mapper.is_ready():
            raise Exception("""Without mapper we are not able to
            recognize schema properly""")
        for table in mapper.list_column():
            table = table.split('.')[0]
            k_table.add(table)
        for entity in mapper.list_entity():
            self.v_ent.add(mapper.get_table(entity))
        k_temp_table = tablenames.difference(self.v_ent)
        for table in k_temp_table:
            if self.get_outdegree(table, self.v_ent) == 0:
                # table doesn't point to a entity
                #     but could point to himself.
                # table not in keyword set
                #     should be on a path of entity ---> attribute
                self.v_attr.add(table)
        self.v_rel = k_temp_table.difference(self.v_attr)

        for link in self.links.values():
            if link.rtable in self.v_attr:
                self.e_attr.add(link.name)
        self.e_rel = set(self.links.keys()).difference(self.e_attr)

    def get_outdegree(self, table, tableset):
        """
        check_outdegree of a table base on the mappered tableset
        """
        outdegree = 0
        for fkey in self.links.values():
            if cmp(fkey.ltable, table) == 0:# outlink from table
                if fkey.rtable in tableset:# point to ent
                    if cmp(fkey.ltable, fkey.rtable) != 0:#dont point to self
                        outdegree = outdegree + 1
        return outdegree

    def handle_alias(self):
        """
        Detect recursive cases, and create Alias table to resolve self
        recursive case.
          1  entity table link to itself
          2  rel table double link to entity table
          3  Error:
                ent table double link to entity table
                    comosite key has been handled by FKCONS
          4  not sure:
                rel table point to itself ? remove?
                ent/rel table point to rel table with double link
                    ---> pick one or both ?
          5  safe to ignore:
                attr table will not involing in path generation
                    any table double link to attr table is fine
                    attr table point to itself
        """
        tempdic = {}
        for node in self.nodelist.values():
            for link in node.outlinks.values():
                if link.rtable in self.v_ent: # 1,2,3
                    if link.rtable == link.ltable:
                        self.set_alias(link)
                    elif tempdic.has_key(link.rtable):
                        if link.ltable in self.v_ent:
                            raise Exception ("""entity table double link
                            to entity table""")
                        self.set_alias(link, tempdic[link.rtable])
                    else:
                        tempdic[link.rtable] = link
                elif link.rtable in self.v_rel: # 4
                    if link.name in self.e_rel:
                        if link.rtable == link.ltable:
                            pass
                        elif tempdic.has_key(link.rtable):
                            pass
                        else:
                            tempdic[link.rtable] = link
            tempdic = {}

    def lookup_link(self, constructor, tables):
        """
        get link sequence from entity to attr
        """
        if constructor:
            ordered = self.ordered
            nodelist = self.nodelist
            nodes = []
            for table in tables:
                if nodelist.has_key(table):
                    if ordered.count(nodelist[table]) != 0:
                        nodes.append(ordered.index(nodelist[table]))
                    else:
                        raise Exception("%s are not exisit in ordered" \
                        % nodelist[table])
                else:
                    raise Exception("%s are not exsit in nodelist" % table)
#            nodes = [ ordered.index(nodelist[table]) for table in tables ]
            subtree = constructor.get_smallest_subtree(nodes)
            for node, parent in subtree.breadth_first():
                if parent != None:
                    yield (ordered[node], ordered[parent])
                else:
                    yield (ordered[node], None)

    def gen_attr_links(self, mapper):
        """
        generate look up table for Entity -> Attribute link.
        this will resolve the issue such as Person table.
        get simplified schema
        we need a function mapper.get_table(column)
        """
        relation = self.get_graph_from_schema()
#        for a_table in self.v_attr:
#            if self.ordered.count(a_table) != 0:
#                self.v_attr.add(self.ordered.index(a_table))

        constructor = ConstructQuery(relation)

        attr_path = {} # {key.attr : [link1, link2, ...]}
        count = 0
        for compkey in mapper.list_key():
            if compkey not in mapper.entdict.keys():
                key, attr = compkey.split('.')
                table1 = mapper.get_table(key)
                table2 = mapper.get_table(compkey)
                if table1 != table2:
                    count = count + 1 # founded link count
                    root = None # start node
                    linkpath = []
                    length = 0
                    for node, parent in self.lookup_link(constructor, \
                            [table1, table2]):
                        if parent is None:
                            root = node
                            continue
                        length = len(linkpath)
                        for link in parent.outlinks.values():
                            if link.rtable == node.name:# parent to node
                                if node.name == table2 and not\
                                        similar(attr, link.lcolumn[0]):
                                # node is attribute node, then
                                # parent.FKColumnName should similar as
                                # attr from compkey
                                    continue
                                linkpath.append(link)
                        if length == len(linkpath):# link is from node to parent
                            for link in node.outlinks.values():
                                if link.rtable == parent.name:
                                    if parent.name == table2 and not\
                                            similar(attr, link.lcolumn[0]):
                                        continue
                                    linkpath.append(link)
                    if root.name == table2:
                        linkpath.reverse()
                    attr_path[compkey] = linkpath
        if len(attr_path) != count:
            raise Exception("""some path are not recognized""")
        return attr_path

    def gen_simschema(self):
        """
        generate simulate schema
        after handle alias and attribute links
            new nodelist
            new links
            update to have new ordered
            fakenode point to original node in new ordered.
        tables and links will not be modified in simschema
        """
        simtables = {}
        for node in self.v_ent:
            simtables[node] = self.nodelist[node]
        for node in self.v_rel:
            simtables[node] = self.nodelist[node]
        simlinks = {}
        for linkname in self.e_rel:
            link = self.links[linkname]
            if link.ltable in simtables and link.rtable in simtables:
                simlinks[linkname] = link
        simschema = TSchema(simtables, simlinks)
        return simschema

    def get_links(self, table):
        """get CLinkObj list for a table"""
        links = []
        for cons in table.constraints:
            if isinstance(cons, ForeignKeyConstraint):
                if cons.name == None:
                    cons.name = self.name_link(cons)
                links.append(self.links[cons.name])
        return links

    def name_link(self, cons):
        """
        naming a constraints without name as table.colname_ftable.colname
        """
        name = cons.table.name
        for idx in range(len(cons.columns)):
            col = cons.columns[idx]
            element = cons.elements[idx]
            name = name + '.' + col.name + "_" + \
                element.target_fullname
        return name

    def check_connective(self):
        """check the connective of the schema"""
        unique_parent = None # checking connective
        for node in self.nodelist.values():
            if unique_parent == None:
                unique_parent = find(node)
            if find(node) != unique_parent:
                return False
        return True

    def add_node(self, node, nodetype):
        """add virtual aliased node"""
        self.nodelist[node.name] = node
        if nodetype == 'attr':
            self.v_attr.add(node.name)
        elif nodetype == 'rel':
            self.v_rel.add(node.name)
        elif nodetype == 'ent':
            self.v_ent.add(node.name)

    def del_node(self, node, nodetype):
        """remove node after named alias"""
        node = self.nodelist[node]
        if nodetype == 'attr':
            self.v_attr.remove(node.name)
        elif nodetype == 'rel':
            self.v_rel.remove(node.name)
        elif nodetype == 'ent':
            self.v_ent.remove(node.name)
        self.nodelist.pop(node.name)

    def add_link(self, link, linktype):
        """add link after named alias"""
        newlink = CLinkObj()
        newlink.set(link.name, [link])
        self.links[link.name] = newlink
        if linktype == 'attr':
            self.e_attr.add(link.name)
        elif linktype == 'rel':
            self.e_rel.add(link.name)
        return newlink

    def del_link(self, link, linktype):
        """remove link after named alias"""
        if linktype == 'attr':
            self.e_attr.remove(link.name)
        elif linktype == 'rel':
            self.e_rel.remove(link.name)
        self.links.pop(link.name)

    def set_alias(self, link1, link2=None):
        """recursive cases"""
        if link2 == None and len (link1.lcolumn) == 1:
            _LOGGER.debug("link to self table %s" % str(link1))
            newnode = "_".join((link1.ltable, link1.lcolumn[0]))
            self.alias_table[newnode] = link1.ltable
            self.atables[newnode] = self.tables[link1.ltable].alias(newnode)
            linkname = newnode + "_FK"
            newlink = LinkObj()
            newlink.set(linkname, link1.ltable, newnode, link1.lcolumn[0], \
                link1.rcolumn[0])
            self.add_link(newlink, 'attr')
            nnode = Node(newnode, [newlink])
            self.add_node(nnode, 'attr')
            self.del_link(link1, 'rel')
        elif len(link2.lcolumn) == 1 and len(link1.lcolumn) == 1:
            _LOGGER.debug("double link to entity table %s %s" % \
                (str(link1), str(link2)))
            v_ent = link1.rtable
            v_rel = link1.ltable
            c_1 = link1.rcolumn[0]
            c_parent = link1.lcolumn[0]
            c_2 = link2.rcolumn[0]
            c_child = link2.lcolumn[0]

            a_parent_child = c_parent + "_" + c_child
            a_child = v_ent + "_" + c_child
            a_child_parent = c_child + "_" + c_parent
            a_parent = v_ent + "_" + c_parent

            self.alias_table[a_parent_child] = v_rel
            self.atables[a_parent_child] = \
                self.tables[v_rel].alias(a_parent_child)
            self.alias_table[a_child_parent] = v_rel
            self.atables[a_child_parent] = \
                self.tables[v_rel].alias(a_child_parent)
            self.alias_table[a_child] = v_ent
            self.atables[a_child] = \
                self.tables[v_ent].alias(a_child)
            self.alias_table[a_parent] = v_ent
            self.atables[a_parent] = \
                self.tables[v_ent].alias(a_parent)


            apc_ve = a_parent_child + "_left_FK"
            apc_vc = a_parent_child + "_right_FK"
            acp_ve = a_child_parent + "_left_FK"
            acp_vp = a_child_parent + "_right_FK"

            newlink1 = LinkObj()
            newlink1.set(apc_ve, a_parent_child, v_ent, c_parent, c_1)
            newlink1 = self.add_link(newlink1, 'rel')

            newlink2 = LinkObj()
            newlink2.set(apc_vc, a_parent_child, a_child, c_child, c_2)
            newlink2 = self.add_link(newlink2, 'attr')

            newlink3 = LinkObj()
            newlink3.set(acp_ve, a_child_parent, v_ent, c_child, c_2)
            newlink3 = self.add_link(newlink3, 'rel')

            newlink4 = LinkObj()
            newlink4.set(acp_vp, a_child_parent, a_parent, c_parent, c_1)
            newlink4 = self.add_link(newlink4, 'attr')

            nnode = Node(a_parent_child, [newlink1, newlink2])
            self.add_node(nnode, 'rel')

            nnode = Node(a_child_parent, [newlink3, newlink4])
            self.add_node(nnode, 'rel')

            nnode = Node(a_child)
            self.add_node(nnode, 'attr')

            nnode = Node(a_parent)
            self.add_node(nnode, 'attr')

            self.del_link(link1, 'rel')
            self.del_link(link2, 'rel')

            self.del_node(v_rel, 'rel')

    def print_schema(self):
        """print schema"""
        banner = "-----------------%s %d--------------"
#        print banner % "tables"
#        pprint(self.tables)
        print banner % ("links", len(self.links))
        pprint(self.links)
        print banner % ("alias_table", len(self.alias_table))
        pprint(self.alias_table)
        print banner % ("nodelist", len(self.nodelist))
        pprint(self.nodelist) #sets for node division
        print banner % ("v_ent", len(self.v_ent))
        pprint(self.v_ent)
        print banner % ("v_attr", len(self.v_attr))
        pprint(self.v_attr)
        print banner % ("v_rel", len(self.v_rel))
        pprint(self.v_rel)
        print banner % ("e_rel", len(self.e_rel))
        pprint(self.e_rel)
        print banner % ("e_attr", len(self.e_attr))
        pprint(self.e_attr)

    def get_table(self, tname):
        """
        get sqlalchemy table object
        handle alias if any, return the real table with alias
        """
        if self.tables.has_key(tname):
            return self.tables[tname]
        elif self.alias_table.has_key(tname):
            return self.atables[tname]
        tname = tname.lower()
        if self.tables.has_key(tname):
            return self.tables[tname]
        elif self.alias_table.has_key(tname):
            return self.atables[tname]
        return None


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
import sqlalchemy

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

    def write_wgraph(self, dot, name="A"):
        """
        output dot graph for this schema, with table name as nodename
        """
        relations = self.get_wgraph_from_schema()
        order = self.ordered
        dot.set_name(name)
        for index in range(len(relations)):
            start_node = relations[index]
            for end_index in start_node:
                dot.add_edge(order[index], order[end_index[0]], end_index[1])
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
        if len(cycles) == 0:
            return False
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
        return True

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
        split could happen on different connectives:
        """
        core_node = set([])
        in_splition = []
        for split in splition:
            if not set(split).issubset(set(self.nodelist.keys())):
                continue
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
        if len(in_splition) == 0:
            return [], []
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

        self.connectives = []

        self.v_ent = set()
        self.v_attr = set()
        self.v_rel = set()
        self.v_orphan = set()

        self.e_rel = set()
        self.e_attr = set()
        self.e_orphan = set()

        self.ordered = []

        self.alias_dict = {} # resolve ora000972 identifier is too long

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
        recognize 4 kinds of node type:
        entity node
        relationship node
        attribute node
        orphan node

        recognize 3 kinds of link type:
        relationship link
        attribute link
        orphan link
        """
        tablenames = set(self.tables.keys())
#        k_table = set()
        if not mapper.is_ready():
            raise Exception("""Without mapper we are not able to
            recognize schema properly""")
#        for table in mapper.list_column():
#            table = table.split('.')[0]
#            k_table.add(table)
        for entity in mapper.list_entity():
            self.v_ent.add(mapper.get_table(entity))
        for nodeset in self.connectives:
            # orphan nodeset
            if nodeset.isdisjoint(self.v_ent):
                self.v_orphan = self.v_orphan.union(nodeset)
                continue
            temptable = nodeset.difference(self.v_ent)
            for table in temptable:
                if self.get_outdegree(table, self.v_ent) == 0:
                    # table doesn't point to a entity
                    #     but could point to himself.
                    # table not in keyword set
                    #     should be on a path of entity ---> attribute
                    self.v_attr.add(table)
            self.v_rel = self.v_rel.union(temptable.difference(self.v_attr))
        for link in self.links.values():
            if link.rtable in self.v_attr:
                self.e_attr.add(link.name)
            if link.rtable in self.v_orphan:
                self.e_orphan.add(link.name)
        self.e_rel = set(self.links.keys()).difference(self.e_attr)\
                                           .difference(self.e_orphan)

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
        attr_path_tables = {} # {key.attr : set([table1, table2,...])
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
                    path_tables = set([])
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
                                path_tables.add(link.ltable)
                                path_tables.add(link.rtable)
                        if length == len(linkpath):# link is from node to parent
                            for link in node.outlinks.values():
                                if link.rtable == parent.name:
                                    if parent.name == table2 and not\
                                            similar(attr, link.lcolumn[0]):
                                        continue
                                    linkpath.append(link)
                                    path_tables.add(link.ltable)
                                    path_tables.add(link.rtable)
                    if root.name == table2:
                        linkpath.reverse()
                    attr_path[compkey] = linkpath
                    attr_path_tables[compkey] = path_tables
        if len(attr_path) != count:
            raise Exception("""some path are not recognized""")
        return attr_path, attr_path_tables

    def gen_simschema(self):
        """
        generate simulate schema
        after handle alias and attribute links
            new nodelist
            new links
            update to have new ordered
            fakenode point to original node in new ordered.
        tables and links will not be modified in simschema
        for each connective generate a separate simschema
        """
        simschemas = []
        idx = 0
        for nodeset in self.connectives:
            simtables = {}
            valid_connective = False
            for node in nodeset:
                if node in self.v_ent:
                    simtables[node] = self.nodelist[node]
                    valid_connective = True
            if valid_connective == False:
                self.connectives.pop(idx)
                continue
            else:
                idx = idx + 1
            for node in self.v_rel:
                if node in nodeset:
                    simtables[node] = self.nodelist[node]
            simlinks = {}
            for linkname in self.e_rel:
                link = self.links[linkname]
                if link.ltable in simtables and link.rtable in simtables:
                    simlinks[linkname] = link
            simschemas.append(TSchema(simtables, simlinks))

        return simschemas

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
        if int("".join(sqlalchemy.__version__.split('.'))[:2]) >= 7:
            for idx in range(len(cons.columns)):
                col = cons.columns[idx]
                element = cons.elements[idx]
                name = name + '.' + col.name + "_" + \
                    element.target_fullname
        else:
            for element in cons.elements:
                for key in cons.columns.keys():
                    col = cons.columns[key]
                    if element.parent == col:
                        name = name + '.' + col.name + "_" + \
                            element.target_fullname
        return name

    def check_connective(self):
        """
        check the connective of the schema
        get connective sets in self.connectives
        """
        parent_list = []
        current_index = 0
        for node in self.nodelist.values():
            parent = find(node)
            if len(parent_list) == 0:
                parent_list.append(parent)
                self.connectives.append(set([parent.name, node.name]))
            if parent == parent_list[current_index]:
                self.connectives[current_index].add(node.name)
            else:
                if parent in parent_list:
                    current_index = parent_list.index(parent)
                    self.connectives[current_index].add(node.name)
                else:
                    current_index = len(parent_list)
                    parent_list.append(parent)
                    self.connectives.append(set([parent.name, node.name]))
        if len(parent_list) != 1:
            _LOGGER.debug(self.connectives)
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

    def check_alias_name(self, alias):
        if alias > 30:
            if alias.count('_') > 1:
                alist = []
                for p in alias.split('_'):
                    if p:
                        alist.append(p[0])
                newalias = '_'.join(alist)
                if self.alias_dict.has_key(newalias):
                    if newalias[-1].isdigit():
                        num = int(newalias[-1])
                        newalias = '%s%d' %(newalias[:-1], num)
                    else:
                        newalias = newalias + '1'
                self.alias_dict[newalias] = alias
                alias = newalias
        return alias

    def set_alias(self, link1, link2=None):
        """recursive cases"""
        if link2 == None and len (link1.lcolumn) == 1:
            _LOGGER.debug("link to self table %s" % str(link1))
            newnode = "_".join((link1.ltable, link1.lcolumn[0]))
            newnode = self.check_alias_name(newnode)
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
            a_parent_child = self.check_alias_name(a_parent_child)
            a_child = v_ent + "_" + c_child
            a_child = self.check_alias_name(a_child)
            a_child_parent = c_child + "_" + c_parent
            a_child_parent = self.check_alias_name(a_child_parent)
            a_parent = v_ent + "_" + c_parent
            a_parent= self.check_alias_name(a_parent)

            _LOGGER.debug("a_parent %s a_child %s" % (a_parent, a_child))

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
        elif self.atables.has_key(tname):
            return self.atables[tname]
        tname = tname.lower()
        if self.tables.has_key(tname):
            return self.tables[tname]
        elif self.alias_table.has_key(tname):
            return self.atables[tname]
        elif self.atables.has_key(tname):
            return self.atables[tname]
        _LOGGER.debug("didn't find table with tname %s" % tname)
        return None

    def set_unique(self, compkey, tname):
        """
        set sqlalchemy table object with a unique name from compkey
        such as dataset.createby : self.tables[tname].alias(dataset_createby)
        """
        if self.atables.has_key(compkey):
            _LOGGER.debug("already set unique for table %s" % tname)
            return
        key = compkey.replace('.', '_')
        _LOGGER.debug("set unique for table %s" % tname)
        if self.tables.has_key(tname):
            self.atables[compkey] = self.tables[tname].alias(key)
            return
        tname = tname.lower()
        if self.tables.has_key(tname):
            self.atables[compkey] = self.tables[tname].alias(key)
            return
        if self.atables.has_key(tname):
            self.atables[compkey] = self.atables[tname]
            return
        raise Exception("compkey %s tname %s are not found in database schema \n%s\n%s\n%s" % \
                (compkey, tname, str(self.alias_dict), str(self.atables.keys()), str(self.tables.keys())))

    def recognize_shortcut(self):
        """
        figure the short cut
        exchange the weight between short cut and passing dependencies
        referential is on primary key.
        dataset<--block<---file
             <------------/
        dataset<----file is a short cut for dataset<--block<--file
        """
        visited = set([]) # visited short_cut
        # Do DFS for each node if a node is founded
        short_cuted = []
        for node in self.v_ent:
            pathes = {} # { end_enitity : [[link1], [link2, link3], ] }
            stack = []
            for link in self.nodelist[node].outlinks:
                stack.append(self.links[link])
                # link.right shouldn't point to itself, need to filter
                # out
            while stack:
                link = stack.pop()
                table = link.rtable
                if table not in self.v_attr and table != node:
#                    and link.rcolumn is in table.primarykey:
                    # if link.left is node then append []
                    # if link.left is not node then append node -->
                    # table
                    new_path = []
                    if link.ltable == node:
                        new_path = [link]
                    else:
                        # trace back
                        for aplink in pathes[link.ltable][0]: # shortest
                            new_path.append(aplink)
                        new_path.append(link)
                    # insert new path to correct position
                    if table not in pathes and table != node:
                        pathes[table] = [new_path]
                    elif len(new_path) > 0:
                        for index in range(len(pathes[table])):
                            if len(new_path) > len(pathes[table][index]):
                                continue
                            distinct = False
                            if len(new_path) == len(pathes[table][index]):
                                for inde in range(len(new_path)):
                                    if new_path[inde] == \
                                        pathes[table][index][inde]:
                                        continue
                                    distinct = True
                            else:
                                distinct = True
                            if distinct:
                                pathes[table].insert(index, new_path)
                for link in self.nodelist[table].outlinks:
                    stack.append(self.links[link])
            # review pathes, print out the short cut
            for table in pathes:
                if len(pathes[table]) > 1:
                    temp = []
                    for path in pathes[table]:
                        strin = ""
                        for link in path:
                            strin += "%s->%s, " % (link.ltable, link.rtable)
                        temp.append(strin)
                    _LOGGER.debug('shortcut found for %s to %s via %s' % \
                    (node, table, str(temp)))
            # update weights for link
            for table in pathes:
                if len(pathes[table]) > 1:
                    if pathes[table][0][0] == pathes[table][1][0]:
                        continue
                    link1 = pathes[table][0][0]
                    link2 = pathes[table][1][0]
                    link3 = pathes[table][1][-1]
                    vis = link1.name + link2.name
                    if not (pathes[table][0][-1] != pathes[table][1][-1] \
                      and pathes[table][0][0] != pathes[table][1][0]):
                        continue
                    short_cuted.append((pathes[table][0],pathes[table][1]))
                    #if vis in visited:
                    #    continue
                    #else:
                    #    visited.add(vis)
                    if link2.weight <= link1.weight and link1.weight < 1:
                        link2.weight = link1.weight + (1 - link1.weight)/2
                    if link3.weight >= link1.weight and link1.weight < 1:
                        link3.weight = link1.weight - (1 - link1.weight)/2
                    _LOGGER.debug('%s.%.5f switch to %s.%.5f' % \
                            (link1, link1.weight, link2, link2.weight))
                    link1.weight, link2.weight = link2.weight, link1.weight
                    link2.weight, link3.weight = link3.weight, link2.weight
        sc_nodeset = []
        for idx in range(len(short_cuted)):
            sc_nodeset.append(set([]))
            for lk in short_cuted[idx][1]:
                sc_nodeset[idx].add(lk.ltable)
                sc_nodeset[idx].add(lk.rtable)
        #print "sc_nodeset", sc_nodeset
        # get all basic cycles on undirected graph
        # for a cycle, calculate node with outdegree == 0 on directed graph
        # then for a cycle with two such nodes,
            # if there is shortcut including,
            # reorganize the link.weight to make sure:
                # 1. path weight to dataset is higher than path weight to files
                # 2. make sure the whole path is selected when all node on this cycle is selected
        relations = self.get_graph_from_schema()
        graph = Graph(relations)
        ugraph = graph.get_undirected()
        cycles = self.get_cycle_basis(ugraph._graph)
        if len(cycles) == 0:
            return False
        nodes = None
        order = self.ordered
        for cycle in cycles:
            # contains outdegree = 0, directed graph
            # contains shortcut 's'
                # get the pathes to outmod and start file, 1
                # get the pathes to outmod and end dataset, 2
                    # sum(1) < sum(2)
                    # sum(1+2) > sum('s') for BFS, min(1,2) > max('s')
            nodes = set([self.ordered[nd].name for nd in cycle])
            is_shortcut = True
            for sc in sc_nodeset:
                if nodes.difference(sc) == set([]):
                    is_shortcut = False
            if not is_shortcut:
                continue
            #print "cycle is", nodes
            tables = set([self.ordered[nd] for nd in cycle])
            degree0 = {}
            for node in cycle:
                tnode = self.nodelist[self.ordered[node].name]
                queue = []
                linkpaths = []
                if self.get_indegree(tnode, tables) == 0:
                    #print tnode
                    for link in tnode.outlinks:
                        linkpath = []
                        #print link,self.links[link].ltable,self.links[link].rtable
                        if self.links[link].rtable in nodes:
                            queue.insert(0, self.nodelist[self.links[link].rtable])
                            linkpath.append(self.links[link])
                            while len(queue) > 0:
                                node = queue.pop()
                                for link in node.outlinks:
                                    if self.links[link].rtable in nodes:
                                        queue.insert(0, self.nodelist[self.links[link].rtable])
                                        linkpath.append(self.links[link])
                        if linkpath != []:
                            linkpaths.append(linkpath)
                if linkpaths != []:
                    degree0[tnode]= linkpaths
            if len(degree0) == 2:
                source1, source2 = degree0.keys()
                s1l1 = degree0[source1][0]
                s1l2 = degree0[source1][1]
                s2l1 = degree0[source2][0]
                s2l2 = degree0[source2][1]
                pathc = None
                pathp = None
                pathcc = None
                pathpc = None
                if len(s1l1) + len(s1l2) > len(s2l1) + len(s2l2):
                    if s1l1[-1].rtable == s2l1[-1].rtable:
                        if len(s1l1) > len(s2l1):
                            pathc = s1l1
                            pathp = s2l1
                            pathcc, pathpc = s1l2, s2l2
                        else:
                            pathcc, pathpc = s1l1, s2l1
                            pathc = s1l2
                            pathp = s2l2
                    else: #s1l1[-1].rtable == s2l2[-1].rtable:
                        if len(s1l1) > len(s2l2):
                            pathc = s1l1
                            pathp = s2l2
                            pathcc, pathpc = s1l2, s2l1
                        else:
                            pathcc, pathpc = s1l1, s2l2
                            pathc = s1l2
                            pathp = s2l1
                else:
                    if s2l1[-1].rtable == s1l1[-1].rtable:
                        if len(s2l1) > len(s1l1):
                            pathc = s2l1
                            pathp = s1l1
                            pathcc, pathpc = s2l2, s1l2
                        else:
                            pathcc, pathpc = s2l1, s1l1
                            pathc = s2l2
                            pathp = s1l2
                    else: #s2l1[-1].rtable == s1l2[-1].rtable:
                        if len(s2l1) > len(s1l2):
                            pathc = s2l1
                            pathp = s1l2
                            pathcc, pathpc = s2l1, s1l2
                        else:
                            pathcc, pathpc = s2l1, s1l2
                            pathc = s2l2
                            pathp = s1l1
                # find path to hierarchical parent node
                # find path to hierarchical child node
                # find path to hierarchical parent to child link, get weight
                base = pathc[-1].weight
                # get the pathes to outmod and start file, 1
                # get the pathes to outmod and end dataset, 2
                    # sum(1) < sum(2)
                    # sum(1+2) > sum('s') for BFS, min(1,2) > max('s')
                pathc[0].weight = base + (1 - base)/4
                pathp[0].weight = base + (1 - base)/3
                pathcc[0].weight = base + (1 - base)/4
                pathpc[0].weight = base + (1 - base)/3

    def get_indegree(self, table, tableset):
        """
        check_indegree of a table base on the tableset
        """
        indegree = 0
        for fkey in self.links.values():
            if cmp(self.nodelist[fkey.rtable], table) == 0:# link to table
                if self.nodelist[fkey.ltable] in tableset:# point to ent
                    indegree = indegree + 1
        return indegree

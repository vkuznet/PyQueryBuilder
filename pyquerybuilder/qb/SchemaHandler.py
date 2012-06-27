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
import time
from collections import deque
from sqlalchemy import select
from sqlalchemy.sql.expression import func

# local modules
from pyquerybuilder.qb.ConstructQuery import ConstructQuery
from pyquerybuilder.qb.NewSchema import OriginSchema
from pyquerybuilder.tools.schema_helper import load_split
from pyquerybuilder.utils.Utils import pull_operator_side, weight_sort
from pyquerybuilder.tools.schema_helper import load_statistics
from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.tools.config import readconfig
#from pyquerybuilder.tools.map_reader import Mapper
#from sqlalchemy.sql.expression import Select

_LOGGER = getLogger("ConstructQuery")


class SchemaHandler(object):
    """
    This object aimes to custom a origin schema to a set of
    sub-schema(sub-graph).
    Schema Handler could iterate sub-schemas to answer a query.
    """
    #def __init__(self, tables, links = None, owner = None):
    def __init__(self, tables, links = None):
        """
        Constructor
        """
        self._schema = OriginSchema(tables)
        self._simschemas = None
        if not self._schema.check_connective():
            _LOGGER.debug('Schema graph is not connective')
        self.attr_path = {}
        self.subconstructors = []
        self.subnodes = [] # calculate coverage
        self.attr_table = set([])

    def recognize_schema(self, mapper, dbmanager=None, db_alias=None):
        """
        # Step 1. Recognize three types of tables and links.
        # Step 2. Detect recursive cases, and create Alias table to
        #         To resolve recursive cases.
        # Step 3. Generate lookup table for Entity -> Attribute link.
        #         This will resolve the issue such as Person table.
        #         generate simplified graph
        # Step 4. Calculate each links type, by default foreign key link
        #         other format of link are acceptable. Such as OUTER
        #         JOIN
        # Step 5. Detect dividings and accept input from administrator.
        #         Load split.yaml file
        # Step 6. Generate sub graphs from each sub sets.
        """
        self._schema.recognize_type(mapper)

        # Step 2. Detect recursive cases, and create Alias table to
        #         To resolve recursive cases.
        #   1. entity table link to itself
        #   2. rel table double link to entity table
        #   3. Error:
        #       . ent table double link to entity table ?
        #           . composite key has been handled by FKCons
        #   4. not sure:
        #       . rel table point to itself ? remove?
        #       . ent/rel table point to rel table with double link
        #       ---> pick one or both ?
        #   5. safe to egnore: 
        #     attr table will not involing in path generation
        #       . any table double link to attr table is fine
        #       . attr table point to itself

        self._schema.handle_alias()
        config = {'alias_mapfile':None, 'split_file':None}
        if dbmanager != None and db_alias != None:
            self.load_statistics(dbmanager, db_alias)
            config = readconfig()
            self.further_map(mapper, config['alias_mapfile'])

        # Step 3. Generate lookup table for Entity -> Attribute link.
        #         This will resolve the issue such as person table.
        #         get simplified graph
        #         We need a function map(key.attribute) ==> table name
        #         on core schema
        self.attr_table = self._schema.v_attr
        self.attr_path = self._schema.gen_attr_links(mapper)
        for name, path in self.attr_path.items():
            for pat in path:
                _LOGGER.debug("path %s is %s.%s --> %s.%s" % (name, \
                pat.ltable, pat.lcolumn, pat.rtable, pat.rcolumn))

        simschemas = self._schema.gen_simschema()

        _LOGGER.debug("%d simschemas are generated" % len(simschemas))
        for simschema in simschemas:
            simschema.update_nodelist()

        if dbmanager != None and db_alias != None:
            self._schema.recognize_shortcut()

        self._simschemas = simschemas

        # Step 4. Calculate each links type, by default foreign key link
        #         other format of link are acceptable. Such as OUTER
        #         JOIN

        # Step 5. Detect dividings and accept input from administrator.
        #         Load split.yaml file
        splition = False
        if dbmanager != None and db_alias != None:
            splition = load_split(config['split_file'])
        if splition:
            for simschema in simschemas:
                self.subconstructors.append([])
                self.subnodes.append([])
                subgraphs, subnodes = simschema.gen_subgraph(splition)
        # Step 6. Generate sub graphs from each sub sets.
        #         self.sub_schema.add(tables)
        #         self.sub_graphs.add(self.graph_from_schema(tables,
        #           links))
        #         ? construct_query instance?
                for subgraph in subgraphs:
                    self.subconstructors[-1].append(\
                      ConstructQuery(subgraph._graph, weighted=True))
                for nodes in subnodes:
                    self.subnodes[-1].append(nodes)
        else:
            for simschema in simschemas:
                graph = simschema.get_wgraph_from_schema()
                self.subconstructors.append([ConstructQuery(graph, weighted=True)])
                nodes = set(range(len(simschema.ordered)))
                self.subnodes.append([nodes])

    def load_statistics(self, dbmanager, db_alias):
        """load statistics"""
        return load_statistics(dbmanager, db_alias, self._schema)

    def further_map(self, mapper, filename="map2.yaml"):
        """further map after alias generated"""
        return mapper.load_mapfile(filename)

    def map_attribute(self, compkey):
        """
        Get the links start from the end node on the core schema
        for this attribute
        """
        _LOGGER.debug("finding attribute link %s" % compkey)
        if self.attr_path.has_key(compkey):
            return self.attr_path[compkey]
        _LOGGER.debug("no attribute link %s" % compkey)
        return None

    def build_query(self, whereclause, keylist, algo="MIS"):
        """
        build query by root join
            check aggregation keywords if querying [key, aggregation, ...]

        """
        start = time.time()
        froms = self.root_join(whereclause, keylist, algo)
        _LOGGER.debug("froms is %s" % str(froms))
        elapsed = (time.time() - start)
        _LOGGER.debug("root_join time %0.5f", elapsed)
        query = self.handle_aggregation(keylist, froms, whereclause)
        return query

    def unique_table_column(self, keylist, index):
        """
        get unique table column at keylist
        index is keyword index at keylist
        """
        tnames = keylist['keyset'][index]
        if tnames.count('.'):
            tname, attr = tnames.split('.')
        if keylist['keyset'].count(keylist['keyset'][index]) > 1\
            and tname in self._schema.v_attr:
            compkey = keylist['keywords'][index]
            self.set_unique(compkey, tname)
            table = self.find_table(compkey)
            if table is not None:
                col = table.columns[attr]
            else:
                raise Error("ERROR can't find table %s" % str(tname))
        else:
            col = self.get_table_column(keylist['mkeywords'][index][0])
        return col

    def single_table_query(self, keylist, froms, whereclause):
        """
        deal with single table queries
        find entity.attr1, entity.attr2, ... [ where entity.attr1 op value ]
        """

    def handle_aggregation(self, keylist, froms, whereclause):
        """
        1. generate selects
        2.
            - if no aggregation contains, gen query
            - if aggregation exists, but not mixed, gen query
        3. handle mixed aggregation by
            -   taking current select as a subquery
            -   apply order_by with all non aggregation keywords
            -   naming this subquery and select all keywords from it
        """
        keywords = keylist['mkeywords']
        # num of tables related in finds
        mtables = set([key.split('.')[0] for key in keylist['keyset']])
        if froms == None and len(mtables) > 1:
            return None
        selects = []
        columns = []
        mix_agg = False
#        for keyword in keywords:
        for index in range(len(keywords)):
            keyword = keywords[index]
            if len(keyword) == 1:
                try:
#                    if keylist['keyset'].count(keylist['keyset'][index]) > 1:
#                        self.set_unique(compkey, tname)
#                        col = self.get_table_column(keylist['keywords'][index])
#                    else:
#                        col = self.get_table_column(keyword[0])
                    col = self.unique_table_column(keylist, index)
                    selects.append(col)
                    columns.append(col)
                    mix_agg = True
                except:
                    _LOGGER.error("can't find table %s" % keyword[0])
                    return None
            elif keyword[1] in ('count', 'max', 'min', 'sum'):
                try:
#                    if keylist['keyset'].count(keylist['keyset'][index]) > 1:
#                        self.set_unique(compkey, tname)
#                        col = self.get_table_column(keylist['keywords'][index])
#                    else:
#                        col = self.get_table_column(keyword[0])
                    col = self.unique_table_column(keylist, index)
                    selects.append(getattr(func, keyword[1])(col))
                    columns.append(col)
                except:
                    _LOGGER.error("can't find table %s" % keyword[0])
                    return None
            else:
                _LOGGER.error("invalid keyword format %s" % str(keyword))
                return None
        if not self.contains_aggregation(keywords) or not mix_agg:
            query = select(selects, from_obj=froms, whereclause=whereclause)
            return query
        bquery = select(columns, from_obj=froms, whereclause=whereclause)
        bquery = bquery.apply_labels().alias()
        keys = bquery.c.keys()
        columns = bquery.columns

        group_by = []
        new_select = []

        for idx in range(len(keywords)):
            keyword = keywords[idx]
            if len(keyword) == 1:
                group_by.append(columns[keys[idx]])
                new_select.append(columns[keys[idx]])
            elif keyword[1] in ('count', 'max', 'min', 'sum'):
                new_select.append(getattr(func, keyword[1])(\
                        columns[keys[idx]]))

        query = select(new_select, group_by=group_by)
        return query

    def contains_aggregation(self, keywords):
        """
        check existence of an aggregation keywords coming with other
        keywords:
            [[key], [key, aggregation], ...]
        """
        for keyword in keywords:
            if len(keyword) > 1:
                return True
        return False

    def check_coverage(self, sim_idx, core_indices):
        """
        check whether this subgraph covering all the tables or not
        to check it, we need the node indexes for each subschema
        if no one matches, return -1
        """
        for idx in range(len(self.subnodes[sim_idx])):
            if core_indices.issubset(self.subnodes[sim_idx][idx]):
                return idx
        return -1

    def construct_query(self, sim_idx, core_indices, algo):
        """
        generate the spanning tree for this table sets
        this function will perform the algorithm on the first matching subgraph
        and return the spanning tree as required
        """
        match_subgraph = self.check_coverage(sim_idx, set(core_indices))
        if match_subgraph == -1:
            _LOGGER.error("no subgraph could answer this query")
            return None
        constructor = self.subconstructors[sim_idx][match_subgraph]
        if algo == 'LWS':
            subtree = constructor.get_leastw_subtree(core_indices)
        elif algo == 'MIS':
            subtree = constructor.get_mcst(core_indices)
        return subtree

    def root_join(self, whereclause, keylist, algo):
        """
        -   keylist including selects and keys in constraints
        -   whereclauses.
        This method:
            - looks through the elements and clauses to determine
                which tables need to be joined in order to support
                the query
            - froms
            - selects generation are suspended
        Algorithm:
            LWS, least weight spanning tree
            MIS, multiple iterator search
        How to deside whether we need extra join?
        """
        tables_of_concern = set()
        # sqlalchemy.sql.expression.Alias or Table
        for keyword in keylist['keyset']:
            try:
                col = self.get_table_column(keyword)
                tables_of_concern.add(col.table)
            except:
                _LOGGER.error("can't find table %s" % keyword[0])
                return None
        # get alias for table
#        if type(whereclause) != type(None):
#            if whereclause.__dict__.has_key('clauses'):
#                for clause in whereclause.clauses:
#                    pull_operator_side(clause, tables_of_concern)
#            else:
#                pull_operator_side(whereclause, tables_of_concern)
#            _LOGGER.debug("tables_of_concern adding clause ones is %s" % \
#                            str(tables_of_concern))

        # no need to take a join if there is only one table involved
        if len(keylist['keyset']) == 1:
            return None

        lens = len(tables_of_concern)
        # find the best candidate spanning tree
        # table_indices is the index list of tables_of_concern
        # referencing self.ordered

        # attribute table should be filter out in table join
        # append attribute table afterwards
        tnames_of_concern = [table.name for table in tables_of_concern]
        _LOGGER.debug("tables_of_concern is %s" % str(tnames_of_concern))
        core_tables = set(tnames_of_concern).difference(self.attr_table)
        _LOGGER.debug("tables on core schema are %s" % str(core_tables))

        #subtree missing the attr_path
        # we could get map_attribute from compkey, which is in query object
        # we take compkey as index for distinguishing the links, such as
        # createdby and modby
        return_jtables = {}
        cons_jtables = {}
        return_jtables, cons_jtables = self.gen_join_table(keylist)
        _LOGGER.debug("return joint table on core schema %s" % \
                str(return_jtables.keys()))
        _LOGGER.debug("cons joint table on core schema %s" % \
                str(cons_jtables.keys()))
        core_tables = core_tables.union(set(return_jtables.keys()))
        core_tables = core_tables.union(set(cons_jtables.keys()))
        _LOGGER.debug("merged core tables are %s " % str(core_tables))
        if len(core_tables) == 1 and lens == 1 and \
            core_tables.issubset(set(tnames_of_concern)):
            return None
        chosen_simschema = self._simschemas[0]
        sim_idx = 0
        if len(self._simschemas) != 1:
            sim_idx = -1
            for idx in range(len(self._simschemas)):
                if core_tables.issubset(self._simschemas[idx].nodelist.keys()):
                    sim_idx = idx
            if sim_idx == -1:
                _LOGGER.error("could not answer this query, please " + \
                "check the relationship between entities")
                return None
        chosen_simschema = self._simschemas[sim_idx]
        core_indices = [chosen_simschema.ordered.index(\
                chosen_simschema.nodelist[tname]) \
                for tname in core_tables]
        subtree = self.construct_query(sim_idx, core_indices, algo)
        _LOGGER.debug("core spanning tree are %s " % str(subtree))
#        print subtree

#        appendix = set(tnames_of_concern).intersection(self.attr_table)

#        print appendix


        if subtree is None:
            _LOGGER.error("Failed to generate a core subtree")
            return None

        # the subtree indicate the order of tables involving the join.
        # but it lose the information on which table is the foreign key,
        # so we need to search through tables to find which had the
        # foreign key and which the primary key
        # root_join is a table.join().join()...
#        print subtree
#        print return_jtables
#        print cons_jtables

        root_join = None
        root_table = self.find_table(\
            chosen_simschema.ordered[subtree.root_index].name)

        unexplored = [(subtree.root_index, None)]
        visited = [False] * len(subtree)
        while(unexplored):
            node_idx, _ = unexplored[0]
            visited[node_idx] = True
            table = self.find_table(\
                chosen_simschema.ordered[node_idx].name)
            if table.name == root_table.name:
                root_join = root_table
#           constraints attribute links
            if table.name in cons_jtables:
                for links, compkey, tname in cons_jtables[table.name]:
                    current = table.name
                    for link in links:
                        if current == table.name:
                            if table.name != link.ltable:
                                root_join = \
                                    self.join_link(root_join, \
                                            link, False, compkey, tname)
                                current = link.ltable
                            root_join = self.join_link(root_join, \
                                            link, True, compkey, tname)
                            current = link.rtable
#           inner nodes
            weight_sort(subtree._graph[node_idx])
            for adjacent in subtree._graph[node_idx]:
                if not visited[adjacent[0]]:
                    unexplored.append((adjacent[0], node_idx))
                    visited[adjacent[0]] = True
                    parent = chosen_simschema.ordered[node_idx]
                    node = chosen_simschema.ordered[adjacent[0]]
                    jlink = None
                    follow_pn = True
                    for link in node.outlinks.values():
                        if link.rtable == parent.name:
                            jlink = link
                            follow_pn = False
                    # attribute link any special?
                    if jlink == None:
                        for link in parent.outlinks.values():
                            if link.rtable == node.name:
                                jlink = link
                    if jlink == None:
                        _LOGGER.error("jlink is None")
                        return None
                    root_join = self.join_link(root_join, jlink, follow_pn)

#           retrive attribute links
            if table.name in return_jtables:
#                print "attribute links"
                for links, compkey, tname in return_jtables[table.name]:
                    current = table.name
                    for link in links:
                        if current != link.ltable:
                            root_join = self.join_link(root_join, \
                                    link, False, compkey, tname)
                            current = link.ltable
                        else:
                            root_join = self.join_link(root_join, \
                                    link, True, compkey, tname)
                            current = link.rtable
            del unexplored[0]
        return root_join

    def join_link(self, root_join, link, direction, compkey=None, tname=None):
        """
        root_join join a link
        direction left to right : True
                  right to left : False
        """
        _LOGGER.debug("join link %s" % str(link))
        if link.ltable == tname:
            ltable = self.find_table(compkey)
        else:
            ltable = self.find_table(link.ltable)
        if link.rtable == tname:
            rtable = self.find_table(compkey)
        else:
            rtable = self.find_table(link.rtable)
        lcol = ltable.c._data[link.lcolumn[0]]
        rcol = rtable.c._data[link.rcolumn[0]]
        if direction:
            root_join = root_join.join(rtable, lcol == rcol)
            _LOGGER.debug("join %s on %s == %s" % \
                (rtable.name, lcol, rcol))
        else:
            root_join = root_join.join(ltable, rcol == lcol)
            _LOGGER.debug("join %s on %s == %s" % \
                (ltable.name, rcol, lcol))
        return root_join

    def gen_join_table(self, keylist):
        """
        get jointable indexed by jointable name
        also record the join type of each jointable
        keywords or constaints
        """
        return_jtables = {}
        cons_jtables = {}
        keylen = len(keylist['keywords'])
        for index in range(keylen):
            compkey = keylist['keywords'][index]
#        for compkey in keylist['keywords']:
            _LOGGER.debug("trying gen join table for %s" % str(compkey))
            links = self.map_attribute(compkey)
            if links == None:
                continue
            _LOGGER.debug("gen join table for %s" % str(links))
            #TODO composite fkkeys
            if links[0].ltable in self._schema.v_ent:
                jointable = links[0].ltable
            else:
                jointable = links[0].rtable
            tname = keylist['keyset'][index]
            if tname.count('.') > 0:
                tname = tname.split('.')[0]
            # set unique alias
            # only set end nodes, which means if double composite on
            # path further handler is needed
            if keylist['keyset'].count(keylist['keyset'][index]) > 1:
                self.set_unique(compkey, tname)
                if not return_jtables.has_key(jointable):
                    return_jtables[jointable] = [(links, compkey, tname)]
                else:
                    return_jtables[jointable].append((links, compkey, tname))
            else:
                if not return_jtables.has_key(jointable):
                    return_jtables[jointable] = [(links, None, None)]
                else:
                    return_jtables[jointable].append((links, None, None))

        for index in range(len(keylist['constraints'])):
            compkey = keylist['constraints'][index]
#        for compkey in keylist['constraints']:
            _LOGGER.debug("trying gen join table for %s" % str(compkey))
            links = self.map_attribute(compkey)
            if links == None:
                continue
            _LOGGER.debug("gen join table for %s" % str(links))
            _LOGGER.debug(links)
            # TODO composite fkkeys
            if links[0].ltable in self._schema.v_ent:
                jointable = links[0].ltable
            else:
                jointable = links[0].rtable
            tname = keylist['keyset'][keylen + index]
            if tname.count('.') > 0:
                tname = tname.split('.')[0]
            if keylist['keyset'].count(keylist['keyset'][keylen + index]) > 1:
                self.set_unique(compkey, tname)
                if not cons_jtables.has_key(jointable):
                    cons_jtables[jointable] = [(links, compkey, tname)]
                else:
                    cons_jtables[jointable].append((links, compkey, tname))
            else:
                if not cons_jtables.has_key(jointable):
                    cons_jtables[jointable] = [(links, None, None)]
                else:
                    cons_jtables[jointable].append((links, None, None))
        return return_jtables, cons_jtables

    def set_unique(self, compkey, tname):
        """set unique sqlalchemy alias for table"""
        self._schema.set_unique(compkey, tname)

    def find_table(self, tname):
        """return sqlalchemy table by table name"""
#        print "get table", tname
        return self._schema.get_table(tname)


    def get_table_column(self, keyword):
        """
        get table or column object from schema
        if the table is in alias table, the real table is return with
            sqlalchemy alias
        """
        if keyword.count('.'):
            (entity, attr) = keyword.split('.')
            table = self.find_table(entity)
            if table is not None:
                if table.columns.has_key(attr):
                    return table.columns[attr]
                attr = attr.lower()
                if table.columns.has_key(attr):
                    return table.columns[attr]
                raise Error("ERROR can't find attribute %s" % str(attr))
            else:
                raise Error("ERROR can't find table %s" % str(entity))
        else:
            entity = keyword
            table = self.find_table(entity)
            if table is not None:
                return table
            else:
                raise Error("ERROR can't find table %s" % str(entity))

    def gen_clauses(self, query, keylist):
        """
        query is a parser result
        correctly analysis the parser result and generate:
            -   select keylist :
                suspending of gen sqla table/column obj
                for handling aggregations
            -   where clause : sqla column.op() obj
        by figure out the required sqlalchemy table/column
        objects.
        """
        whereclause = None
        stack = []
        queue = deque([])
        constraint = None
        if query.has_key('constraints'):
            stack.append(query['constraints'])
            constraint = stack.pop()
        else:
            return whereclause
        # sort out the sequence by usin a stack and a queue
        while constraint:
            if type(constraint) is type([]):
                if len(constraint) == 1:
                    # operate miss
                    constraint = constraint[0]
                    stack.append(constraint)
                else:
                    multiple = False
                    for index in range(0, len(constraint)):
                        cons = constraint[index]
                        if type(cons) is type ('str'):
                            if multiple == True:
                                stack.pop()
                            stack.append(cons)
                            stack.append(constraint[index-1])
                            stack.append(constraint[index+1])
                            multiple = True
            elif type(constraint) is type({}):
                queue.append(constraint)
            elif type(constraint) is type('str'):
                queue.append(constraint)
            if len(stack) == 0:
                break
            constraint = stack.pop()
        # now we get correct sequence in queue
        constraint = queue.popleft()
        if len(queue) == 0:
            try:
#                column = self.get_table_column(constraint['keyword'][0])
                column = self.unique_table_col(keylist, constraint['keyword'])
            except:
                _LOGGER.error("can't find table %s" % \
                        constraint['keyword'][0])
                return None
            whereclause = column.op(constraint['sign'])(constraint['value'])
            return whereclause
        # right use as right hand to hold constraint
        right = None
        # left use as left hand to hold constraint
        left = None
        # extra use as A B C or and in queue
        extra = None
        while constraint:
            if type(constraint) is type({}):
                if right is None:
                    right = constraint
                elif left is None:
                    left = constraint
                elif extra is None:
                    extra = right
                    right = left
                    left = constraint
                else:
                    _LOGGER.error("consecutive constraint > 3 in queue")
                    return None
            elif type(constraint) is type('str'):
                if right is not None and left is not None:
                    # construct whereclause
                    if type(right) == type({}):
                        try:
#                            column = self.get_table_column(right['keyword'][0])
                            column = self.unique_table_col(keylist, right['keyword'])
                        except:
                            _LOGGER.error("can't find table %s" % \
                                right['keyword'][0])
                            return None
                        right = column.op(right['sign'])(right['value'])
                    if type(left) == type({}):
                        try:
#                            column = self.get_table_column(left['keyword'][0])
                            column = self.unique_table_col(keylist, left['keyword'])
                        except:
                            _LOGGER.error("can't find table %s" % \
                                left['keyword'][0])
                            return None
                        left = column.op(left['sign'])(left['value'])
                    if constraint == 'and':
                        whereclause = (left & right)
                    elif constraint == 'or':
                        whereclause = (left | right)
                    left = None
                    right = whereclause
                    if extra:
                        left = right
                        right = extra
                        extra = None
            if len(queue) == 0:
                break
            constraint = queue.popleft()
        return whereclause

    def unique_table_col(self, keylist, keyword):
        """
        get unique table column at keylist
        """
        tnames  = keyword[0]
        compkey = keyword[1]
        if tnames.count('.'):
            tname, attr = tnames.split('.')
        if keylist['keyset'].count(tnames) > 1\
            and tname in self._schema.v_attr:
            self.set_unique(compkey, tname)
            table = self.find_table(compkey)
            if table is not None:
                col = table.columns[attr]
            else:
                raise Error("ERROR can't find table %s" % str(tname))
        else:
            col = self.get_table_column(tnames)
        return col

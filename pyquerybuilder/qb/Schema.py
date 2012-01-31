#!/usr/bin/env python

"""
This class reads sqlalchemy schema metadata in order to construct
joins for an arbitrary query.
"""

__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.11 $"

# system modules
from logging import getLogger
from sqlalchemy import MetaData, Column, select
#from sqlalchemy.sql.expression import Select

# local modules
from pyquerybuilder.qb.ConstructQuery import ConstructQuery

_LOGGER = getLogger("ConstructQuery")

def pull_operator_side(clause, tables_of_concern):
    """
    Add clause into table.
    """
    if clause.__dict__.has_key('left'):
        if issubclass(clause.left.__class__, Column):
            tables_of_concern.add(clause.left.table)
    if clause.__dict__.has_key('right'):
        if issubclass(clause.right.__class__, Column):
            tables_of_concern.add(clause.right.table)

def find_table_name(schema, name):
    """
    Find person_table in given schema.
    """
    person_tables = []
    for table_name in schema.tables:
        if table_name.lower() == name.lower():
            person_tables.append(table_name)
    if len(person_tables)>1:
        raise Exception, "More than one person table %s." % (person_tables,)
    elif len(person_tables) == 0:
        return None
    return person_tables[0]

def find_table(schema, name):
    """
    Find table object for given name, schema.
    """
    person_tables = []
    for table_name in schema.tables:
        if table_name.lower() == name.lower():
            person_tables.append(schema.tables[table_name])
    if len(person_tables) > 1:
        raise Exception, "More than one person table %s." % (person_tables,)
    elif len(person_tables) == 0:
        return None
    return person_tables[0]

class Schema(object):
    """
    This object is created around a sqlalchemy MetaData object. When given
    a sqlalchemy select object in build_query, it constructs determines how to
    join tables from the MetaData to support the query.
    """
    def __init__(self, tables, foreign_keys = None, owner = None):
        """
        Constructor
        """
        class MySchema(object):
            """class encapsulate tables structure"""
            def __init__(self, tables):
                """initialize tables"""
                self.tables = tables
        # The dictionary keys disagree with table names. Make them agree.
        table_dict = {}
        for table_name in tables:
            table = tables[table_name]
            table_dict[table.name] = table
        self._schema = MySchema(table_dict)
        self._ordered = None
        person_table = 'person'
        if owner:
            self._owner = owner.lower()
        else:
            self._owner = owner
        self._foreign_tables = {}
        self._person_table = find_table(self._schema, person_table)

        if self._person_table:
            to_exclude = set([self._person_table])
        else:
            to_exclude = set()
        connectivity = self.graph_from_schema(self._schema,
              self.make_foreign_keys(foreign_keys, self._schema), to_exclude)
        self.construct_query = ConstructQuery(connectivity)
        self.outers = [('seblock.blockid', 'block.id'),
                     ('block.id', 'seblock.blockid')]

    def build_query(self, query):
        """build query by root_join"""
        root_join = self.root_join(query)
        if query != root_join:
            query.append_from(root_join)
        return query

    def build_query_with_sel(self, sel, query, add_join = None):
        """extral root_join.join with add_join """
        root_join = self.root_join(query)
        if add_join:
            for item in add_join:
                table, l_col, r_col = item
                root_join = root_join.join(table, l_col == r_col)
        sel.append_from(root_join)
        return sel

    def root_join(self, query):
        '''
        Query is a sqlalchemy query with select elements and where clauses.
        This method:

            - looks through the elements and clauses to determine
              which tables need to be joined in order to support the query.
            - adds those joins to the query and returns it.
        '''

        tables_of_concern = set()
        # col.table returns a select statement. We want the metadata table.
        # This is unsupported in sqlalchemy!
        # Todo I need verify this.
#        for col in query._raw_columns:
#            tables_of_concern.add(col.table)
        for table in query.froms:
            tables_of_concern.add(table)
        if  query.__dict__.has_key('whereclause'): # SQLAlchemy 0.3
            where_clause = query.whereclause
        elif query.__dict__.has_key('_whereclause'): # SQLAlchemy 0.4 0.5
            where_clause = query._whereclause
        else:
            raise Exception, "Query '%s' does not contain whereclause" % query
        if where_clause:
            if where_clause.__dict__.has_key('clauses'):
                for clause in where_clause.clauses:
                    pull_operator_side(clause, tables_of_concern)
            else:
                pull_operator_side(where_clause , tables_of_concern)

        # No need to calculate joins if there is only one table involved.
        # We actually make mistakes if that single table is Person.
        if len(tables_of_concern) == 1:
            return query

        # Remove Person table because it is not in any spanning trees.
        block_use_person_table = False
        if self._person_table in tables_of_concern:
            tables_of_concern.remove(self._person_table)
            block_use_person_table = True

        # Find the smallest spanning tree containing tables 
        #      for SELECT and WHERE.
        # table_indices is the index list of table concerns 
        #      references to self._ordered
        table_indices = [self._ordered.index(table)
                                for table in tables_of_concern]

        subtree = self.construct_query.get_smallest_subtree(table_indices)
        if subtree is None:
            return None
        _LOGGER.debug("Schema.build_query: query tree length %d" %
                                               (subtree.get_nodes_number(), ))
        _LOGGER.debug("Schema.build_query: query tree itself %s" %
                                                           (subtree, ))

        # The subtree tells us the order of tables in the join, but it loses
        # information on which table is the foreign key, so we need to search
        # through tables to find which had the foreign key and which the
        # primary key.
        # root_join is a table.join().join()....
        root_join = None
        for (node_idx, parent_idx) in subtree.breadth_first():
            if parent_idx is None:
                root_table = self._ordered[node_idx]
                root_join = root_table
                if block_use_person_table and root_table.c.has_key('CreatedBy'):
                    root_join = root_join.join(self._person_table,
                              root_table.c.CreatedBy == self._person_table.c.ID)
            else:
                if node_idx in self._foreign_tables[parent_idx]:
                # table has a f_key to parent
                    (l_col, r_col) = self._foreign_tables[parent_idx][node_idx]
                elif parent_idx in self._foreign_tables[node_idx]:
                # parent table has a f_key to this table
                    (r_col, l_col) = self._foreign_tables[node_idx][parent_idx]
                # special case: 
                # block to seblock == 1 we outerjoin seblock 
                # seblock to block == 0 we join block, block table is huge
                if self.outers.count((str(l_col).lower(), str(r_col).lower())):
                    root_join = root_join.outerjoin(r_col.table, l_col == r_col)
                else:
                    root_join = root_join.join(r_col.table, l_col == r_col)
#                root_join = root_join.join(r_col.table, l_col==r_col)
        return root_join
#        query.append_from(root_join)
#        return query


    def make_foreign_keys(self, foreign_keys, schema):
        """ input: foreign_keys and schema
            output: foreign_keys
            when input foreign_keys not exists, it is generated from schema by
            { table:table.foreign_keys, ...}
        """
        if not foreign_keys:
            foreign_keys = {}
            for table_name in schema.tables:
                table = schema.tables[table_name]
                foreign_keys[table] = table.foreign_keys
        return foreign_keys

    def graph_from_schema(self, metadata, table_fks, exclude = set()):
        """
        Build graph with edges for provided SQLAlchemy MetaDta object;
        list of foreign keys and set of exclude tables.
        """
        #_ordered is a list version of metadata.tables.values() 
        #         and we can set exclude table list
        self._ordered = [metadata.tables[table_name]
                            for table_name in metadata.tables
                            if metadata.tables[table_name] not in exclude]
        # contains all foreign keys linked table index in ordered_names
        relations = []
        # ordered_names which is the list version of fullname self._ordered
        # VK, use names rather then compare tables objects
        ordered_names = []
        for item in self._ordered:
#            ordered_names.append(item.fullname)
            ordered_names.append(item.name)
        exclude_names_list = []
        for table in exclude:
#            exclude_names_list.append(table.fullname)       
            exclude_names_list.append(table.name)
        exclude_names = set(exclude_names_list) # set of exclude table name
        order_list = list(ordered_names)   # list of table_name in _ordered
        order_list.sort()
#        print "\n\nSchema:"
#        print order_list
#        print exclude_names
#        print "owner",self._owner
        try:
            search_name = None
            # traversing the tables 
            #   for each foreign_keys in this table: 
            #     find correspond table index in ordered_names(self._ordered) 
            #   relations store set of thoses f_key_index 
            #   self._foreign_tables[table_index] store {f_key_index:FK, ...}
            for table_index in xrange(0, len(self._ordered)):
                table = self._ordered[table_index]
                foreign_keys = table_fks[table]
                index_set = set()
                short_tables = {}
                for f_key in foreign_keys:
                    if f_key.column.table in exclude:
                        # table linked by foreign keys not in exclude list
                        continue

                    search_name = f_key.column.table
                    if search_name.name in exclude_names:
                        # table.fullname are not in exclude list 
                        continue
#                    f_key_index = self._ordered.index(search_name)
                    f_key_index = ordered_names.index(search_name.name)
                    index_set.add(f_key_index)
                    short_tables[f_key_index] = (f_key.parent, f_key.column)

                relations.append(index_set)
                self._foreign_tables[table_index] = short_tables
                # foreign_tables stores 
                # {table_index:{f_key_index:(f_key.parent,f_key.colum),...},...}
        except ValueError, value_err:
            print value_err
            _LOGGER.error("""Schema.GraphFromSchema ValueError %s.
                    Could not find f_key.column.table %s in
                    self._ordered %s. Len(ordered)=%d
                    Len(metadata.tables)=%d""" % (str(value_err),
                    search_name, self._ordered, len(self._ordered),
                    len(metadata.tables)))
            raise Exception(
                "Could not find the table for a given foreign key constraint.",
                '''Constraint table %s len(ordered)=%d len(metadata.tables)=%d
                ordered=%s''' % (search_name, len(self._ordered),
                len(metadata.tables), str([xdx.name for xdx in self._ordered])))
        return relations

    def write_graph(self, dot, name = "A"):
        """output the path in connectivity"""
        connectivity = self.graph_from_schema(self._schema,
                                 self.make_foreign_keys(None, self._schema))
        order = self._ordered
        dot.set_name(name)
        for start_node_idx in range(0, len(connectivity)):
            start_node = connectivity[start_node_idx]
            for end_node_idx in start_node:
                dot.add_edge(order[start_node_idx], order[end_node_idx])
        dot.finish_output()

def make_view_without_table(metadata, rid_name, rid_replace):
    '''
    The subroutine looks through all tables in metadata, copying them
    to the new metadata instance. When it finds a table has a foreign
    key to the rid_table, it creates a view of that table where the
    foreign keys are replaced by the rid_replace column from the rid_table.

    For example, rid_name='Person', rid_replace='FullName'.
    Input:

        - metadata = sqlalchemy.MetaData
        - rid_name = String name of table.
        - rid_replace = String column name of column to use from rid_table

    Returns new MetaData object containing only the tables we want.
    '''
#    new_md = MetaData(metadata.name+"view")
    new_md = MetaData()
    rid_table = metadata.tables[rid_name]
    # traversing tables in current metadata.
    # if table not to be replaced then find out the one from it's FK.
    #    { parent.name : (rid_table.alias(parent.name),f_key), ....}
    #  if we do find some
    # 
    #    traversing each column:
    #      rid_table.alias(f_key.parent.fullname).c[rid_replace].label(col.name)
    #    make new joins
    #       new_join_table = table.join(rid_table.alias(f_key.parent.fullname)
    #    create view 
    #        select(elements, from_obj = [new_join_table], use_labels)
    #    add new view into new_md
    #    new_md.tables[table_name + 'view'] = view.alias(table_name
    #                     + 'view')
    #         f_key.parent == rid_table.alias(
    #                      f_key.parent.fullname).c[f_key.column.name])
    for table_name in metadata.tables:
        if table_name == rid_name:
            continue
        table = metadata.tables[table_name]

        # list the foreign keys we will replace
        replace_alias = {}
        for f_key in table.foreign_keys:
            # f_key.column.table point to the reference table
            # this f_key.parent points which node?
            if f_key.column.table == rid_table:
#                replace_alias[f_key.parent.name] = (
#                             rid_table.alias(f_key.parent.name), f_key)
                # rid_table got new alias as rid_table.c[''].fullname
#       fullname was replaced by name,
                fullname = "%s_%s" % (f_key.parent.table.name,
                                      f_key.parent.name)
                replace_alias[fullname] = (
                            rid_table.alias(fullname), f_key)
#        print "foreignkey: \n"
#        for f in replace_alias:
#            print "    name:", f
#            x =  replace_alias[f]
#            print"        values: ", x[0].name, x[1]

#        print "\n"
        if replace_alias:
            # make all columns for new view
            elements = []
            for col in table.c:
                fullname = "%s_%s" % (table.name, col.name)
                if replace_alias.has_key(fullname):
                    (alias_t, f_key) = replace_alias[fullname]
#                if replace_alias.has_key(col.name):
#                    (alias_t, f_key) = replace_alias[col.name]
                    # rid_table.c[rid_replace] as rid_table.c[''].name
                    elements.append(alias_t.c[rid_replace].label(col.name))
                else:
                    elements.append(col.label(col.name))

            # make joins for the new view
            aliases = replace_alias.keys()
            join_name = aliases[0]
            (join_table, f_key) = replace_alias[join_name]
            new_join_table = table.join(join_table,
                              f_key.parent == join_table.c[f_key.column.name])
            for join_name in aliases[1:]:
                (join_table, f_key) = replace_alias[join_name]
                new_join_table = new_join_table.join(join_table,
                         f_key.parent == join_table.c[f_key.column.name])

            # create the view
            view = select(elements, from_obj = [new_join_table],
                                use_labels = True)

            new_md.tables[table_name + "View"] = view.alias(table_name
                           + "View")
        else:
            new_md.tables[table_name + "View"] = table.alias(table_name
                           + "View")
#        print "%s elements: \n" % table_name
#        print [ e.name for e in elements]
#        print "\n"


    # Now construct our new foreign keys which refer only to View tables.
    # We can't actually change the foreign key in sqlalchemy, so we keep
    # a separate list.
    class FK:
        """Foreign key colum,parrent"""
        def __init__(self, col, par):
            """initiallize"""
            self.column = col
            self.parent = par
        def outputs(self):
            """output values"""
            print "%s from %s" % (self.column, self.parent)


    foreign_keys = {}
    # traversing each table in new meat_data
    #   traversing f_key in table
    #      fro = table.c[f_key.parent.fullname]
    #      des  = new_md.tables[f_key.column.table.fullname + 
    #                               "View"].c[f_key.column.name]
#    for table_name in new_md.tables:
#        print "table: ", table_name
#        print "value: ", new_md.tables[table_name]
    for table_name in new_md.tables:
        table = new_md.tables[table_name]
        table_keys = set()
        for f_key in table.foreign_keys:
            fro = table.c[f_key.parent.name]
#       fullname was replaced by name
#            fro = table.c[f_key.parent.fullname]
            des = new_md.tables[f_key.column.table.name +
                  "View"].c[f_key.column.name]
#            des = new_md.tables[f_key.column.table.fullname + 
#                               "View"].c[f_key.column.name]
            table_keys.add(FK(des, fro))
        foreign_keys[table] = table_keys
#    print "foreign_keys: \n"
#    for f in foreign_keys:
#        print "    name :", f.name
#        for x in foreign_keys[f]:
#            print "        values :", x.outputs()
#    print "\n"

    return (new_md, foreign_keys)


#!/usr/bin/env python

"""
Assistant for viewing schema modification and apply further modifciation:
    view original schema graph
    view simulate schema graph
    specify indirect map, such as dataset.parent
    view basic cycles in simulate schema graph
    view core ambiguous graph generate from simulate schema graph
    specify split file
        view the splition result based on the split file
As a result, generate an unified configuration file
        or generate all necessary configuration files
"""
import os
from math import log
from optparse import OptionParser
from subprocess import check_call, Popen, PIPE
import glob
#from sqlalchemy.sql.expression
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.qb.DotGraph import DotGraph, MultiDot
from pyquerybuilder.qb.NewSchema import OriginSchema
from pyquerybuilder.utils.Utils import load_file
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.qb.Graph import Graph
from pyquerybuilder.qb.WGraph import WGraph


def check_indexed(columns, indexes):
    """
    check table.indexes and find whether it could cover all the
    columns or not
    """
    cols = columns[:]
    for index in indexes:
        for col in index.columns:
            if col.name in cols:
                cols.remove(col.name)
    return len(cols) == 0


def load_statistics(dbmanager, db_alias, originschema):
    """
    load statistics for simulate schema
    DBManager
    No need to collect all the statistics
    such as the attribute table
    T(R) = "select count(col) from TABLE"
    S(R, r) = "select count(distinct col1, col2) from TABLE"
    join column in FK:
                link.rcolumn is primary key
                link.rcolumn has index
    given a link, find out whether it's referencing that.
    table_size:
    column_distinct:
    """
    table_size = {}
    #index_info = {}
    select_info = {}
    tables = originschema.tables
    select = "SELECT COUNT(%s) FROM %s"
    select_c = "SELECT COUNT(DISTINCT %s) FROM %s"
# Calculate table size
    for tname, table in tables.items():
#   SQLAlchemy 0.5.8
#        select_ts = select % (','.join(table.primary_key.keys()), tname)
#   SQLAlchemy 0.6 0.7
        select_ts = select % \
            ('*', tname)

        if dbmanager.db_type[db_alias] == 'oracle' and \
            dbmanager.db_owner[db_alias]:
            select_ts = select % ('*', \
            dbmanager.db_owner[db_alias].lower() + '.' + tname)

        size = dbmanager.execute(select_ts, db_alias).fetchone().values()
        table_size[tname] = size[0]
# Handle alias table
    for tname, table in originschema.alias_table.items():
        table_size[tname] = table_size[table]
# Calculate Link
#        index info
#        primary info
    for link in originschema.links.values():
        tname = link.rtable
        if originschema.alias_table.has_key(tname):
            tname = originschema.alias_table[tname]
        columns = link.rcolumn
        table = tables[tname]
        if check_indexed(columns, table.indexes):
            select_info[link.name] = 1
            continue

        if len(columns) == 1:
#   SQLAlchemy 0.5.8
#            if columns[0] in table.primary_key.keys():
#   SQLAlchemy 0.6 0.7
            if columns[0] in table.primary_key.columns.keys():
                select_info[link.name] = 1
                continue
            select_cd = select_c % (columns[0], tname)

            if dbmanager.db_type[db_alias] == 'oracle' and \
                dbmanager.db_owner[db_alias]:
                select_cd = select_c % (columns[0], \
                    dbmanager.db_owner[db_alias].lower() + '.' + tname)

        else:
            select_cd = select_c % (",".join(columns), tname)

            if dbmanager.db_type[db_alias] == 'oracle' and \
                dbmanager.db_owner[db_alias]:
                select_cd = select_c % (",".join(columns), \
                    dbmanager.db_owner[db_alias].lower() + '.' + tname)

        size = dbmanager.execute(select_cd, db_alias).fetchone().values()[0]
        distinct = 0
        if table_size[tname] != 0:
            distinct = size/table_size[tname]
        select_info[link.name] = distinct
        link.indexed = 0

    # assign weight on links
    ieffects = 1
    for lname, link in originschema.links.items():
        sums = table_size[link.ltable] + \
            table_size[link.rtable] * select_info[lname] + 4
        link.weight = 1 - (1/log(sums, 2)) + (1 - link.indexed) * ieffects
#        print link.ltable, '-->', link.rtable, link.weight

def load_split(filename=None):
    """
    load split file from configration directory
    """
    if filename == None:
        filename = 'split.yaml'
    if not os.path.isfile(filename):
        return False
    return load_file(filename)

def write_splition(simschema, splition, filename="Subgraph"):
    """
    try load_split
    generate subgraphs
    write subgraphs
    """
    splition = load_split(splition)
    if splition == False:
        return None
    order = simschema.ordered
    subgraphs, _ = simschema.gen_subgraph(splition)
    multidot = MultiDot(filename)
    for graph in subgraphs:
        nodes = graph._graph
        dot = multidot.get_dot()
        for index in range(len(nodes)):
            start_node = nodes[index]
            for end_node in start_node:
                dot.add_edge(order[index], order[end_node[0]])
        dot.finish_output()

def write_original_schema_graph(oschema, filename="originalschema"):
    """view original schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    oschema.write_graph(dot, filename)

def write_simulate_schema_graph(simschema, filename="simschema"):
    """view simulate schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    simschema.write_wgraph(dot, filename)

def write_basics_cycles(simschema, filename="basic_cycle"):
    """view basics cycles in simulate schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    return simschema.write_cyclic_graph(dot, filename)

def write_core_graph(simschema, filename="coreschema"):
    """view core graph on simulate schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    relations = simschema.get_graph_from_schema()
    graph = Graph(relations)
    ugraph = graph.get_undirected()
    cycles = simschema.get_cycle_basis(ugraph._graph)
    nodes = set([])
    order = simschema.ordered
    for cycle in cycles:
        nodes = nodes.union(set(cycle))
    for node in nodes:
        start_node = relations[node]
        for end_node in start_node:
            if end_node in nodes:
                dot.add_edge(order[node], order[end_node[0]], end_node[1])
    dot.finish_output()

def write_core_wgraph(simschema, filename="coreschema"):
    """view core graph on simulate schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    relations = simschema.get_wgraph_from_schema()
    wgraph = WGraph(relations)
    core = wgraph.get_core_graph()
    order = simschema.ordered
    nodes = set([])
    for node in range(len(core)):
        if core[node] != []:
            nodes.add(node)
#            for end_node in core[node]:
#                dot.add_edge(order[node], order[end_node[0]], end_node[1])
    for node in nodes:
        start_node = relations[node]
        for end_node in start_node:
            if end_node[0] in nodes:
                dot.add_edge(order[node], order[end_node[0]], end_node[1])
    dot.finish_output()

def main():
    """
    main
        view original schema graph
        view simulate schema graph
        specify indirect map, such as dataset.parent
        view basic cycles in simulate schema graph
        view core ambiguous graph generate from simulate schema graph
        specify split file
        view the splition result based on the split file
    """
    usage = "usage: %prog -u <database link> -m <mapfile> \n"
    usage += "      --view_origin \n"
    usage += "      --view_simulate \n"
    usage += "      --alias_mapfile=<mapfile with alias tables> \n"
    usage += "      --view_basic_cycles \n"
    usage += "      --view_core_graph \n"
    usage += "      --divide_by=<file specify the splition of core graph> \n"
    usage += "      --view_splition \n"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-u", "--url", action="store", type="string",
          dest="url", help="input database connect url")
    parser.add_option("-m", "--mapfile", action="store", type="string",
          dest="mapfile", help="input registration yaml map file")
    parser.add_option("-o", "--view_origin", action="store_true",
          dest="view_origin", help="view origin schema graph")
    parser.add_option("-s", "--view_simulate", action="store_true",
          dest="view_simulate", help="view simulate schema graph")
    parser.add_option("-a", "--alias_mapfile", action="store", type="string",
          dest="alias_mapfile", help="input mapfile based on aliased table")
    parser.add_option("-b", "--view_basic_cycles", action="store_true",
          dest="view_basics", help="view basic cycles on simulate schema graph")
    parser.add_option("-c", "--view_core_graph", action="store_true",
          dest="view_core", help="view core ambiguous graph on simulate graph")
    parser.add_option("-d", "--divide_by", action="store", type="string",
          dest="split_file", help="input split file and do dividing")
    parser.add_option("-r", "--view_splition", action="store_true",
          dest="view_splition", help="view splition graph")

    url = ""
    mapper = Mapper()
#    mapfile = os.path.join(os.path.dirname(sys.argv[0]), 'map.yaml')
    mapfile = ""
    splition_file = None

    (options, _) = parser.parse_args()

    if not options.url:
        parser.error("database url is needed to do schema review")
    url = options.url
    dbmanager = DBManager()
    dbmanager.connect(url)
    dbalias = dbmanager.get_alias(url)
    tables = dbmanager.load_tables(dbalias)
    originschema = None
    simschema = None
    originschema = OriginSchema(dbmanager.db_tables[dbalias])

    if not originschema.check_connective():
        print "schema graph is not connective"
#        raise Exception('Schema graph is not connective')

    if options.view_origin:
        write_original_schema_graph(originschema, "original_schema")
        check_call(['dot', '-Tpng', 'original_schema.dot', '-o', \
            'original_schema.png'])

    if not options.mapfile:
        print "further review need mapfile"
        return

    mapfile = options.mapfile
    mapper.load_mapfile(mapfile)
    if dbmanager.db_type[dbalias] == 'mysql':# for mysql case sensitive
        mapper.set_sens(True)

    if not mapper.validate_map(tables):
        raise Exception("conflicts between map file and schema")

    originschema.recognize_type(mapper)
    originschema.handle_alias()
    originschema.gen_attr_links(mapper)
    load_statistics(dbmanager, dbalias, originschema)

    if options.alias_mapfile:
        mapper.load_mapfile(options.alias_mapfile)


    simschemas = originschema.gen_simschema()
    for simschema in simschemas:
        simschema.update_nodelist()

    originschema.recognize_shortcut()

    if options.view_simulate:
        for idx in range(len(simschemas)):
            simschema = simschemas[idx]
            fname = 'simschema%d.png' % idx
            if len(simschema.nodelist) > 1:
                write_simulate_schema_graph(simschema, 'simschema')
                check_call(['dot', '-Tpng', 'simschema.dot', '-o', fname])

    if options.view_basics:
        for idx in range(len(simschemas)):
            simschema = simschemas[idx]
            if len(simschema.nodelist) < 2:
                continue
            if not write_basics_cycles(simschema, "basic_cycle%d" % idx):
                continue
            fname = 'basic_cycle%d_pack.png' % idx
            p1 = Popen(["dot"] + glob.glob('basic_cycle%d_*.dot' % idx), \
                stdout=PIPE)
            p2 = Popen(["gvpack"], stdin=p1.stdout, stdout=PIPE)
            p3 = Popen(['dot', '-Tpng', '-o', fname], \
                stdin=p2.stdout, stdout=PIPE)
            p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            p2.stdout.close()
            output = p3.communicate()[0]

    if options.view_core:
        for idx in range(len(simschemas)):
            simschema = simschemas[idx]
            if len(simschema.nodelist) < 2:
                continue
            write_core_wgraph(simschema)
            fname = 'coreschema%d.png' % idx
            check_call(['dot', '-Tpng', 'coreschema.dot', '-o', fname])

    if options.split_file:
        splition_file = options.split_file

    if options.view_splition:
        for idx in range(len(simschemas)):
            simschema = simschemas[idx]
            if len(simschema.nodelist) < 2:
                continue
            write_splition(simschema, splition_file, "Subgraph%d" % idx)
            fname = 'subgraph%d_pack.png' % idx
            p1 = Popen(["dot"] + glob.glob('Subgraph%d_*.dot' % idx), \
                stdout=PIPE)
            p2 = Popen(["gvpack"], stdin=p1.stdout, stdout=PIPE)
            p3 = Popen(['dot', '-Tpng', '-o', fname], \
                stdin=p2.stdout, stdout=PIPE)
            p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            p2.stdout.close()
            output = p3.communicate()[0]

if __name__ == '__main__':
    main()
#python schema_helper.py -m ../../etc/map.yaml -u
#    mysql://dbs:cmsdbs@liangd.ihep.ac.cn:3316/CMS_DBS -a
#    ../../etc/map2.yaml -d ../../etc/split.yaml -r

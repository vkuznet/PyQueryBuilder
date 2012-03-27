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


def load_statistics(dbmanager, alias, originschema):
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
    select = "select count(%s) from %s"
    select_c = "select count(distinct %s) from %s"
# Calculate table size
    for tname, table in tables.items():
#   SQLAlchemy 0.5.8
#        select_ts = select % (','.join(table.primary_key.keys()), tname)
#   SQLAlchemy 0.6 0.7
        select_ts = select % \
            (','.join(table.primary_key.columns.keys()), tname)
        size = dbmanager.execute(select_ts, alias).fetchone().values()
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
        else:
            select_cd = select_c % (",".join(columns), tname)
        size = dbmanager.execute(select_cd, alias).fetchone().values()[0]
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
    simschema.write_graph(dot, filename)

def write_basics_cycles(simschema, filename="basic_cycle"):
    """view basics cycles in simulate schema graph"""
    fns = filename + '.dot'
    fls = open(fns, 'w')
    dot = DotGraph(fls)
    simschema.write_cyclic_graph(dot, filename)

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
                dot.add_edge(order[node], order[end_node])
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
    usage += "      --view_basics_cycles \n"
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
    if not options.url or not options.mapfile:
        parser.error("database url and mapfile is needed to do schema review")
    url = options.url
    mapfile = options.mapfile

    mapper.load_mapfile(mapfile)
    dbmanager = DBManager()
    dbmanager.connect(url)
    dbalias = dbmanager.get_alias(url)
    tables = dbmanager.load_tables(dbalias)
    originschema = None
    simschema = None

    if not mapper.validate_map(tables):
        raise Exception("conflicts between map file and schema")

    originschema = OriginSchema(dbmanager.db_tables[dbalias])

    if not originschema.check_connective():
        raise Exception('Schema graph is not connective')

    originschema.recognize_type(mapper)
    originschema.handle_alias()
    originschema.gen_attr_links(mapper)
    load_statistics(dbmanager, dbalias, originschema)

    if options.view_origin:
        write_original_schema_graph(originschema, "original_schema")
        check_call(['dot', '-Tpng', 'original_schema.dot', '-o', \
            'original_schema.png'])

    if options.alias_mapfile:
        mapper.load_mapfile(options.alias_mapfile)

    simschema = originschema.gen_simschema()
    simschema.update_nodelist()

    if options.view_simulate:
        write_simulate_schema_graph(simschema, 'simschema')
        check_call(['dot', '-Tpng', 'simschema.dot', '-o', \
            'simschema.png'])

    if options.view_basics:
        write_basics_cycles(simschema)
        p1 = Popen(["dot"] + glob.glob('basic_cycle_*.dot'), stdout=PIPE)
        p2 = Popen(["gvpack"], stdin=p1.stdout, stdout=PIPE)
        p3 = Popen(['dot', '-Tpng', '-o', 'basic_cycle_pack.png'], \
            stdin=p2.stdout, stdout=PIPE)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.stdout.close()
        output = p3.communicate()[0]

    if options.view_core:
        write_core_graph(simschema)
        check_call(['dot', '-Tpng', 'coreschema.dot', '-o', \
            'coreschema.png'])

    if options.split_file:
        splition_file = options.split_file

    if options.view_splition:
        write_splition(simschema, splition_file, "Subgraph")
        p1 = Popen(["dot"] + glob.glob('Subgraph_*.dot'), stdout=PIPE)
        p2 = Popen(["gvpack"], stdin=p1.stdout, stdout=PIPE)
        p3 = Popen(['dot', '-Tpng', '-o', 'subgraph_pack.png'], \
            stdin=p2.stdout, stdout=PIPE)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.stdout.close()
        output = p3.communicate()[0]

if __name__ == '__main__':
    main()
#python schema_helper.py -m ../../etc/map.yaml -u
#    mysql://dbs:cmsdbs@liangd.ihep.ac.cn:3316/CMS_DBS -a
#    ../../etc/map2.yaml -d ../../etc/split.yaml -r

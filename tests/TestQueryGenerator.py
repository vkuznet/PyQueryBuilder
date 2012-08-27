#!/usr/bin/env python
"""
generate test queries based on the QL keywords from Mapper
"""
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.qb.NewSchema import OriginSchema
from pyquerybuilder.tools.schema_helper import load_statistics
from optparse import OptionParser
from copy import copy
import pprint
p = pprint.PrettyPrinter(indent=4)
def main():
    usage = "usage: %prog -m mapfile \n"
    usage += "      -s databaselink -a alias_mapfile\n"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-m", "--mapfile", action="store", type="string",
          dest="mapfile", help="input registration yaml map file")
    parser.add_option("-s", "--source", action="store", type="string",
          dest="source", help="input validate database source link")
    parser.add_option("-a", "--alias_mapfile", action="store", type="string",
          dest="alias_mapfile", help="input mapfile based on aliased table")

    mapper = Mapper()
    mapfile = None
    dbmanager = None
    source = None
    originschema = None
    simschema = None

    (options, args) = parser.parse_args()
    if options.mapfile:
        mapfile = options.mapfile
    if options.source:
        source = options.source


    if mapfile == None or source == None:
        print "mapfile and source is needed"
        return

    mapper.load_mapfile(mapfile)
    dbmanager = DBManager()
    dbmanager.connect(source)
    dbalias = dbmanager.get_alias(source)
    tables = dbmanager.load_tables(dbalias)

    columns = mapper.list_column()
    entities = mapper.list_entity()
    keys = mapper.list_key()
    edict = {}
    edict = gendict(mapper)
   #gen single
    gen_single(edict)
    samples = get_sample(mapper, dbmanager, dbalias)

#    if dbmanager.db_type[dbalias] == 'mysql':# for mysql case sensitive
#        mapper.set_sens(True)
    originschema = OriginSchema(dbmanager.db_tables[dbalias])
    originschema.check_connective()
    originschema.recognize_type(mapper)
    originschema.handle_alias()
#    print originschema.alias_table
    samples = get_sample(mapper, dbmanager, dbalias, originschema.alias_table)
#    print samples

    originschema.gen_attr_links(mapper)
    load_statistics(dbmanager, dbalias, originschema)

    if options.alias_mapfile:
        mapper.load_mapfile(options.alias_mapfile)
    edict = gendict(mapper)
    single = gen_single(edict)
    writedown(single, 'single.txt')
    singlec = gen_single_constraints(edict, single, mapper, samples)
    writedown(singlec, 'singlec.txt')

    double = gen_double(edict)
#    p.pprint (double)
    doublec = gen_double_constraints(edict, double, mapper, samples)
    writedown(doublec, 'doublec.txt')

#    simschemas = originschema.gen_simschema()
#    for simschema in simschemas:
#        simschema.update_nodelist()

def writedown(lists, fn):
    fd = open(fn, 'w')
    for li in lists:
        if type(li) == type(tuple):
            li = li[0]
        fd.write(li + '\n')
    fd.close()

def gendict(mapper):
    columns = mapper.list_column()
    entities = mapper.list_entity()
    keys = mapper.list_key()
    edict = {}
    for entity in entities:
        edict[entity] = []
    for key in keys:
        ent = None
        attr = None
        if key.find('.') == -1:
            ent = key
        else:
            ent, attr = key.split('.')
        if attr:
            edict[ent].append("%s.%s"%(ent,attr))
#    p.pprint(edict)
    return edict

def gen_single(edict):
    """gen list"""
    single = []
    for ent in edict:
        query = "find "
        for attr in edict[ent]:
            query += attr + ', '
        query = query.rstrip(', ')
        single.append(query)
#    p.pprint(single)
    return single

def gen_double(edict):
    """
    gen list
    how to know distence?
    """
    double = []
    pairs = []
    entlist = edict.keys()
    lens = len(entlist)
    for index1 in range(lens):
        for index2 in range(lens):
            if index1 < index2:
                pairs.append((entlist[index1], entlist[index2]))
#    print len(pairs)
#    p.pprint(pairs)
    for pair in pairs:
        query = "find "
        templist = copy(edict[pair[0]])
        templist.extend(edict[pair[1]])
        for attr in templist:
            query += attr + ', '
        query = query.rstrip(', ')
        double.append((query, pair))
    return double

def get_sample_walias(mapper, alias, dbmanager, dbalias):
    """get sample after alias mapping"""
    samples = {}
    columns = mapper.list_column()

def get_sample(mapper, dbmanager, dbalias, alias=None):
    """ """
    samples = {}
    columns = mapper.list_column()
    entities = mapper.list_entity()
    keys = mapper.list_key()
    tables = {}
    tm = "SELECT %s FROM ( SELECT %s FROM %s ORDER BY dbms_random.value ) WHERE rownum = 1"
    owner = ""
    if dbmanager.db_owner.has_key(dbalias):
        owner = '"' + dbmanager.db_owner[dbalias] + '".'
    # generate a column lists for a table
    column_list = {}
    for column in columns:
        table, col = column.split('.')
        if alias != None:
            if alias.has_key(table.lower()):
                table = alias[table.lower()]
        if not column_list.has_key(table):
            column_list[table] = []
        column_list[table].append(col)
    for column in columns:
        table, col = column.split('.')
        if alias != None:
            if alias.has_key(table.lower()):
                table = alias[table.lower()]
    for table, cols in column_list.items():
        columns = ""
        for col in cols:
            columns += col + ','
        if len(cols) > 0:
            columns = columns.rstrip(',')
        query = tm % (columns, columns, owner + table)
#        print query
        res = dbmanager.execute(query, db_alias=dbalias).fetchone()
        for idx in range(len(cols)):
            a = "NULL"
            if res != None:
                if res[idx] != None:
                    a = res[idx]
                    if type(a) == type(str) and a.index(" ") != -1:
                        a = '"%s"' % a
            samples[cols[idx]] = a
    print samples
    return samples

def sample(dbmanager, dbalias, column):
    """
    SELECT logical_file_name FROM
    ( SELECT logical_file_name FROM CMS_DBS.FILES
    ORDER BY dbms_random.value )
    WHERE rownum = 1 ;
    """

def gen_single_constraints(edict, single, mapper, samples):
    """gen single constraints"""
    constraints = []
    sample_data = "NULL"
    for query in single:
        ent = query.split('find')[1].lstrip().split('.')[0]
        for attr in edict[ent]:
            col = mapper.get_column(attr)
            table, col = col.split('.')
            if samples.has_key(col):
                sample_data = samples[col]
            if sample_data != "NULL":
                constraints.append(query + ' where ' + attr + ' = ' + str(sample_data))
    p.pprint(constraints)
    return constraints

def gen_double_constraints(edict, double, mapper, samples):
    """gen double constraints"""
    constraints = []
    sample_data = "NULL"
    for query, pair in double:
        attrs =  copy(edict[pair[0]])
        attrs.extend(edict[pair[1]])
        for attr in attrs:
            col = mapper.get_column(attr)
            table, col = col.split('.')
            if samples.has_key(col):
                sample_data = samples[col]
            if sample_data != "NULL":
                constraints.append(query + ' where ' + attr + ' = ' + str(sample_data))
    p.pprint(constraints)
#    print len(constraints)
    return constraints

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
perform map between QL key and table.column
"""
import os, sys
import pprint
from yaml import load as yamlload
from logging import getLogger
from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.tools.schema_loader import SchemaLoader
from optparse import OptionParser
_LOGGER = getLogger("ConstructQuery")

class Mapper(object):
    """mapper between QL key and table.column"""
    def __init__(self):
        """initialize mapper"""
        self.dict = {}
        self.tbdict = {}
        self.coldict = {}
        self.entdict = {}
        self.mapfile = None
        self.pp = pprint.PrettyPrinter(indent=4)

    def load_mapfile(self, filename):
        """load map file"""
        if filename == None:
            raise Error('argments can not be None')
        if not os.path.isfile(filename):
            raise Error('map file %s does not exists' % filename)
        map_file = file(filename)
        map_yaml = yamlload(map_file)
#        print map_yaml
        _LOGGER.debug("load map_yaml %s"% str(map_yaml))
        tempdict = {}
        for key in map_yaml.keys():
            if map_yaml[key] is None:
                raise Error("Entity has none attribute.")
            for tempdict in map_yaml[key]:
                if len(tempdict) != 1:
                    raise Error("Format error when specify a attribute")
                attr = tempdict.keys()[0]
                if tempdict[attr] is None:
                    continue
#                    raise Error("Table.Column is missing for %s.%s" % (key, attr))
                names = tempdict[attr].split('.')
                full_keyword = '.'.join([key,attr])
                if len(names) != 2:
                    raise Error("table.column format error")
                else:
                    self.dict[full_keyword] = tempdict[attr]
                    #self.tbdict[key] = names[0].lower()
                    self.tbdict[full_keyword] = names[0]
                    self.coldict[full_keyword] = names[1]
                if not self.dict.has_key(key):
                    self.dict[key] = tempdict[attr]
                    self.tbdict[key] = names[0]
                    self.coldict[key] = names[1]
                    self.entdict[key] = tempdict[attr]
        self.mapfile = filename

    def is_ready(self):
        """Check map file is loaded and mapper is initialized"""
        if self.mapfile != None and self.dict != {} :
            return 1
        return 0

    def validate_map(self, sorted_tables):
        """validate loaded map from DBManager"""
#        tables = {}
#        for table in sorted_tables:
#            tables[table.name] = table
        tables = sorted_tables
        for key in self.tbdict.keys():
            if not tables.has_key(self.tbdict[key]):
                raise Error("table %s doesn't exist" % self.tbdict[key])
            else:
                table = tables[self.tbdict[key]]
                if not table.columns.has_key(self.coldict[key]):
                    raise Error("column %s doesn't exist in table %s "% \
                          ( self.coldict[key], self.tbdict[key]))
        return True

    def has_key(self, key):
        """verify we have key in mapper"""
        return self.dict.has_key(key)

    def get_key(self, column):
        """get key from column seldomly use"""
        for item in self.dict.items():
            if item[1] == column:
                return item[0]

    def get_column(self, key):
        """get column from key"""
        if self.has_key(key):
            return self.dict[key]

    def get_table(self, key):
        """get table for a given key"""
        if self.has_key(key):
            return self.tbdict[key]

    def list_key(self):
        """list key"""
        temp = self.dict.keys()
        temp.sort()
        return temp

    def list_column(self):
        """list column"""
        return set(self.dict.values())

    def list_entity(self):
        """list entity"""
        temp = self.entdict.keys()
        temp.sort()
        return temp

    def pprint(self, arg):
        """pretty print"""
        self.pp.pprint(arg)

def main():
    """main """
    usage = "usage: %prog -m mapfile \n"
    usage += "      -v --validate_mapfile=<mapfile> --source=<database link>\n"
    usage += "      --find_key=<table|table.column> --find_column=<key> \n"
    usage += "      --find_table=<key> --list_key --list_column --list_entity"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-m", "--mapfile", action="store", type="string",
          dest="mapfile", help="input registration yaml map file")
    parser.add_option("-v", "--validate", action="store_true",
          dest="validate", help="perform validation for the mapping")
    parser.add_option("-f", "--validate_mapfile", action="store", type="string",
          dest="vmapfile", help="input validate mapfile")
    parser.add_option("-s", "--source", action="store", type="string",
          dest="source", help="input validate database source link")
    parser.add_option("-k", "--find_key", action="store", type="string",
          dest="find_key", help="input table/column to get corresponding key ")
    parser.add_option("-c", "--find_column", action="store", type="string",
          dest="find_column", help="input key to get table[.column] ")
    parser.add_option("-t", "--find_table", action="store", type="string",
          dest="find_table", help="input key to get only table name ")
    parser.add_option("-e", "--list_key", action="store_true",
          dest="list_key", help="list all keys ")
    parser.add_option("-o", "--list_column", action="store_true",
          dest="list_column", help="list all tables/columns")
    parser.add_option("-i", "--list_entity", action="store_true",
          dest="list_entity", help="list all entity ")

    mapper = Mapper()
    mapfile = os.path.join(os.path.dirname(sys.argv[0]), 'map.yaml')
    validate = False
    column = None
    key = None
    list_key = False
    list_column = False
    list_entity = False
    vmap = None
    sloader = SchemaLoader()
    dbmanager = None
    source = None

    (options, args) = parser.parse_args()
    if options.mapfile:
        mapfile = options.mapfile
    if options.validate:
        validate = options.validate
        if options.vmapfile:
            vmap = options.vmapfile
        elif options.source:
            source = options.source
        else:
            parser.error("options -v need either mapfile or source")
    if options.find_key:
        column = options.find_key
    if options.find_column:
        key = options.find_column
    if options.find_table:
        key = options.find_table
    if options.list_key:
        list_key = options.list_key
    if options.list_column:
        list_column = options.list_column
    if options.list_entity:
        list_entity = options.list_entity

    mapper.load_mapfile(mapfile)

    if validate:
        if vmap:
            tables = sloader.load_from_file(vmap).sorted_tables
            if mapper.validate_map(tables):
                print "Validate is OK"
        else:
            dbmanager = DBManager()
            dbmanager.connect(source)
            dbaliase = dbmanager.get_alias(source)
            tables = dbmanager.load_tables(dbaliase).values()
            if mapper.validate_map(tables):
                print "Validate is OK"
    if column:
        mapper.pprint(mapper.get_key(column))
    if key:
        if options.find_column:
            mapper.pprint(mapper.get_column(key))
        if options.find_table:
            mapper.pprint(mapper.get_table(key))
    if list_key:
        mapper.pprint(mapper.list_key())
    if list_column:
        mapper.pprint(mapper.list_column())
    if list_entity:
        mapper.pprint(mapper.list_entity())


if __name__ == '__main__':
    main()


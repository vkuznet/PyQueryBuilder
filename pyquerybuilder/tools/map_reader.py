#!/usr/bin/env python
"""
perform map between QL key and table.column
"""
import os, sys
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
        self.mapfile = None

    def load_mapfile(self, filename):
        """load map file"""
        if filename == None:
            raise Error('argments can not be None')
        if not os.path.isfile(filename):
            raise Error('map file %s does not exists' % filename)
        map_file = file(filename)
        map_yaml = yamlload(map_file)
#        print map_yaml
        _LOGGER.debug("loag map_yaml %s"% str(map_yaml))
        for key in map_yaml.keys():
            if map_yaml[key] is None:
                raise Error("table.column is None")
            else:
                names = map_yaml[key].split('.')
                if len(names) != 2:
                    raise Error("table.column format error")
                else:
                    self.tbdict[key] = names[0].lower()
                    self.coldict[key] = names[1]
        self.mapfile = filename
        self.dict = map_yaml

    def is_ready(self):
        """Check map file is loaded and mapper is initialized"""
        if self.mapfile != None and self.dict != {} :
            return 1
        return 0

    def validate_map(self, sorted_tables):
        """validate loaded map"""
        tables = {}
        for table in sorted_tables:
            tables[table.name] = table
#        print self.tbdict.keys()
#        print tables.keys()
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

    def list_key(self):
        """list key"""
        return self.dict.keys()

    def list_column(self):
        """list column"""
        return self.dict.values()

def main():
    """main """
    usage = "usage: %prog -m mapfile \n"
    usage += "      -v --validate_mapfile=<mapfile> --source=<database link>\n"
    usage += "      --find_key=<table|table.column> --find_column=<key> \n"
    usage += "      --list_key --list_column"
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
          dest="find_column", help="input key to get table/column ")
    parser.add_option("-e", "--list_key", action="store_true",
          dest="list_key", help="list all keys ")
    parser.add_option("-o", "--list_column", action="store_true",
          dest="list_column", help="list all tables/columns")

    mapper = Mapper()
    mapfile = os.path.join(os.path.dirname(sys.argv[0]), 'map.yaml')
    validate = False
    column = None
    key = None
    list_key = False
    list_column = False
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
    if options.list_key:
        list_key = options.list_key
    if options.list_column:
        list_column = options.list_column

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
        print mapper.get_key(column)
    if key:
        print mapper.get_column(key)
    if list_key:
        print mapper.list_key()
    if list_column:
        print mapper.list_column()


if __name__ == '__main__':
    main()


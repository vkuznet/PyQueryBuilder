#!/usr/bin/env python
"""
perform map between QL key and table.column
"""
import os, sys 
from yaml import load as yamlload
from logging import getLogger
from pyquerybuilder.utils.Errors import Error
from UnittestDB import UnittestDB
_LOGGER = getLogger("ConstructQuery")

class Mapper(object):
    """mapper between QL key and table.column"""
    def __init__(self):
        """initialize mapper"""
        self.dict = {}
        self.tbdict = {}
        self.coldict = {}

    def load_mapfile(self, filename):
        """load map file"""
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
        self.dict = map_yaml
        
    def validate_map(self, metadata):
        """validate loaded map""" 
        sorted_tables = metadata.sorted_tables
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
def usage():
    """usage for map_reader"""
    prog_name = os.path.basename(sys.argv[0])
    print "Usage:"
    print "python %s --validate_map=<map> --mapfile=<mapfile> " % prog_name
    print "  --find_key=<table|table.column> --find_column=<key> "
    print "  --list_key --list_column"
    print " "

if __name__ == '__main__':
    MAPPER = Mapper()
    MAPFILE = 'testmap.yaml'
    COLUMN = None
    KEY = None
    LIST_KEY = False
    LIST_COLUMN = False
    VMAP = None
    UDB = UnittestDB()

    for ARG in sys.argv[1:]:
        ARG = str.split(ARG, "=")
        if ARG[0] == "--mapfile":
            MAPFILE = ARG[1]
        elif ARG[0] == "--find_key":
            COLUMN = ARG[1]
        elif ARG[0] == "--find_column":
            KEY = ARG[1]
        elif ARG[0] == "--list_key":
            LIST_KEY = True
        elif ARG[0] == "--list_column":
            LIST_COLUMN = True
        elif ARG[0] == "--validate_map":
            VMAP = ARG[1]
        else:
            print "Ignoring unrecognized argument: %s" % ARG
    if not VMAP:
        usage()
        sys.exit(1)
    MAPPER.load_mapfile(MAPFILE)
    if COLUMN:
        print MAPPER.get_key(COLUMN)
    elif KEY:
        print MAPPER.get_column(KEY)
    elif LIST_KEY:
        print MAPPER.list_key()
    elif LIST_COLUMN:
        print MAPPER.list_column()
    elif VMAP:
        if MAPPER.validate_map(UDB.load_from_file(VMAP)):
            print "Validate is OK"

  

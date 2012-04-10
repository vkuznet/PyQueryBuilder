#!/usr/bin/env python
"""
QueryBuilder
"""


#import traceback
from logging import getLogger
import time

from sqlalchemy import MetaData

from pyquerybuilder.qb.SchemaHandler import SchemaHandler
#from pyquerybuilder.db.DBManager import DBManager, print_list
#from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.parser import qparse
from pyquerybuilder.tools.schema_loader import load_from_file

_LOGGER = getLogger("ConstructQuery")

def query_parser(mapper, in_put):
    """
    1.perform parser on input query
    2.perform keyword to table[.column] mapping
    3.return mapped query dictionary
        {'keywords':{}, 'constraints':{}}
      keylist also return to be used in
                appending attribute link
                titles?
    """
    keylist = {'keywords':[], 'constraints':[]}
    presult = qparse.parse(in_put)
    if presult == None:
        _LOGGER.error("parser result is empty")
        return None, None
    _LOGGER.debug("""query dictionary before mapping %s""" % \
                            str(presult))
    # do mapping
    keywords =  presult['keywords']
    for keyword in keywords:
        if mapper.has_key(keyword[0]):
            keylist['keywords'].append(keyword)
            key = mapper.get_column(keyword[0])
            keyword.remove(keyword[0])
            keyword.insert(0, key)

        else:
            _LOGGER.error("""keyword not in mapper %s""",
                       str(keyword[0]))
            return None, None

    constraint = None
    if presult.has_key('constraints'):
        constraint = presult['constraints']
    stack = []
    while (constraint):
        # push all constraint on [] into stack
        if type(constraint) is type([]):
            for con in constraint:
                stack.append(con)

        cons = stack.pop()
        # we find a constraint do mapper
        if type(cons) is type({}):
            keyword = cons['keyword']
            if mapper.has_key(keyword[0]):
                keylist['constraints'].append(keyword[0])
                key = mapper.get_column(keyword[0])
                cons['keyword'] = [key]
            else:
                _LOGGER.error("""keyword %s not in mapper """,
                       str(keyword[0]))
                return None, None
            # we finished the last element in stack
            if len(stack) == 0:
                break
            constraint = stack.pop()
        # we find a [] put it in constraint
        elif type(cons) is type([]):
            constraint = cons

    _LOGGER.debug("""user input is: %s""" % str(in_put))
    _LOGGER.debug("""parse result is: %s""" % str(presult))
    return presult, keylist

class QueryBuilder():
    """Application QueryBuilder"""
    def __init__(self, verbose = 0):
        """initialize"""
        class MySchema(object):
            """class encapsulate tables structure"""
            def __init__(self, tables=None):
                """initialize """
                self.tables = tables

            def set_tables(self, tables):
                """set tables"""
                self.tables = tables

            def is_loaded(self):
                """tables loaded"""
                if self.tables != None:
                    return 1
                return 0

        self.schema = MySchema()
        self.querybuilder = None
        self.mapper = None
        self.keywords = []

    def is_ready(self):
        """check schema/mapfile is loaded"""
        if self.querybuilder != None:
            if self.schema.is_loaded() :
                if self.mapper != None :
                    if self.mapper.is_ready():
                        return 1
                print "map file is not loaded"
                return 0
            print "schema is not loaded"
        return 0

    def set_mapper(self, mapfile='map.yaml'):
        """set mapper"""
        self.mapper = Mapper()
        self.mapper.load_mapfile(mapfile)

    def set_from_tables(self, tables):
        """set querybuilder from tables"""
        self.schema.set_tables(tables)
        self.querybuilder = SchemaHandler(tables)

    def set_from_files(self, schema_file):
        """set querybuilder from schema file"""
        metadata = MetaData()
        tables = None
        metadata = load_from_file(schema_file)
        tables = metadata.tables
#        self.schema = metadata
        self.schema.set_tables(tables)
        self.querybuilder = SchemaHandler(tables)

    def recognize_schema(self, dbmanager=None, alias=None):
        """recognize schema"""
        self.querybuilder.recognize_schema(self.mapper, dbmanager, alias)

    def parse_input(self, in_puts):
        """parse input"""
        return query_parser(self.mapper, in_puts)

    def generate_sqlalchemy_clauses(self, query):
        """generate sqlalcemy query"""
        if query is None:
            return None
        return self.querybuilder.gen_clauses(query)

    def build_query(self, query):
        """
        build query for dbsh
        """
        query, keylist = self.parse_input(query)
        whereclause = self.generate_sqlalchemy_clauses(query)
        query = self.querybuilder.build_query(whereclause, keylist)
        return query


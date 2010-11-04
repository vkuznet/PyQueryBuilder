#!/usr/bin/env python
"""
QueryBuilder
"""


import traceback
from collections import deque
from logging import getLogger
from optparse import OptionParser

from sqlalchemy import select, MetaData
#from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import func

from pyquerybuilder.qb.Schema import Schema, find_table
from pyquerybuilder.db.DBManager import DBManager, print_list
from pyquerybuilder.utils.Errors import Error
from pyquerybuilder.tools.map_reader import Mapper
from pyquerybuilder.parser import qparse
from  pyquerybuilder.tools.schema_loader import load_from_file
#from pyquerybuilder.qb.ConstructQuery import ConstructQuery



_LOGGER = getLogger("ConstructQuery")

def get_table_column(metadata, keyword):
    """get table or column object from schema"""
    if keyword.count('.'):
        (entity, attr) = keyword.split('.')
        table = find_table(metadata, entity)
        if table:
            return table.columns[attr]
        else: 
            raise Error("ERROR can't find table %s" % str(entity))
    else:
        entity = keyword
        table = find_table(metadata, entity)
        if table:
            return table
        else: 
            raise Error("ERROR can't find table %s" % str(entity))


def generate_query(metadata, query):
    """generate query from parse result"""
    if query:
        key_list = []
        for keyword in query['keywords']:
            if len (keyword) == 1:
                key_list.append(get_table_column(metadata, keyword[0]))
            elif keyword[1] in ('count', 'max', 'min', 'sum'):
                key_list.append( \
        getattr(func, keyword[1])(get_table_column(metadata, keyword[0])))
            else:
                raise Error(\
                "ERROR: invalid keyword format %s" % str(keyword))

        whereclause = None
        stack = []
        queue = deque([])
        constraint = None
        if query.has_key('constraints'):
            stack.append(query['constraints'])
            constraint = stack.pop()
        else:
            return  select(key_list, whereclause)
        # sort out the sequence by using a stack and a queue        
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
                        if type(cons) is type('str'):
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
        # Now we have correct sequence in queue
#        print queue
        constraint = queue.popleft()
        if len(queue) == 0:
            column = get_table_column(metadata, constraint['keyword'][0])
            whereclause = column.op(constraint['sign'])(constraint['value'])
            return  select(key_list, whereclause)
        # right use as right hand to hold constraint
        right = None
        # left use as left hand to hold constraint
        left = None
        # extra use as A B C or and in queue
        extra = None
        while constraint:
            if type(constraint) is type({}):
                if right is None :
                    right = constraint
                elif left is None:
                    left = constraint
                elif extra is None:
                    extra = right
                    right = left
                    left = constraint
                else:
                    raise Error("ERROR: consecutive constraint >3 in queue")
            elif type(constraint) is type('str'):
                if right and left :
                    # construct whereclause
                    if type(right) == type({}):
                        column = get_table_column(metadata, right['keyword'][0])
                        right = column.op(right['sign'])(right['value'])
                    if type(left) == type({}):
                        column =  get_table_column(metadata, left['keyword'][0])
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
#                print whereclause
#        print "type whereclause is ", type(whereclause)
        return  select(key_list, whereclause)                            



def test_query_parser(mapper, in_put):
    """input query ==parse==> output dictionary 
       ==mapper==> select sentences"""
    presult = qparse.parse(in_put)
    if presult == None:
        raise Error("parse result is empty")
#    print "parse result: ", presult 
    # construct a query 
    keywords =  presult['keywords']
    for keyword in keywords:
        if mapper.has_key(keyword[0]):
            key = mapper.get_column(keyword[0])
#            print "%s ==map==> %s"% (keyword[0], key)
            keyword.remove(keyword[0])
            keyword.insert(0, key)

        else:
            _LOGGER.error("""keyword not in mapper %s""", 
                       str(keyword[0]))
            raise Error(\
              "ERROR: keyword not in mapper %s" % str(keyword[0]))
            
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
                key = mapper.get_column(keyword[0])
                cons['keyword'] = [key]
#                print "%s ==map==> %s"% (keyword[0], key)
            else: 
                _LOGGER.error("""keyword not in mapper %s""",
                       str(keyword[0]))
                raise Error("ERROR: keyword not in mapper %s"\
                         % str(keyword[0]))
            # we finished the last element in stack
            if len(stack) == 0:
                break
            constraint = stack.pop()
        # we find a [] put it in constraint
        elif type(cons) is type([]):
            constraint = cons

    _LOGGER.debug("""user input is: %s""" % str(in_put))
    _LOGGER.debug("""parse result is: %s""" % str(presult))
#    print presult
    return presult

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
        self.querybuilder = Schema(tables)

    def set_from_files(self, schema_file):
        """set querybuilder from schema file"""
        metadata = MetaData()
        tables = None
        metadata = load_from_file(schema_file)
        tables = metadata.tables
#        self.schema = metadata
        self.schema.set_tables(tables)
        self.querybuilder = Schema(tables)
           
    def parse_input(self, in_puts):
        """parse input"""
        return test_query_parser(self.mapper, in_puts)
    
    def generate_sqlalchemy_query(self, query):
        """generate sqlalcemy query"""
#    print type(process_dataset.c.Name)
#    print type(process_dataset.columns['Name'])
        return generate_query(self.schema, query)
    
    def build_query(self, query):
        """build query"""
#    print "query._raw_columns is ", select_test._raw_columns
#    print "query.inner_columns is ", [col for col in select_test.inner_columns]
#    print "query.froms is ", select_test.froms
#    print dir(select_test)
        keys = query.split('find')[1].split('where')[0].split(',')
        keywords = [x.strip() for x in keys ]
        mquery = test_query_parser(self.mapper, query)
        self.keywords = keywords
        mquery = generate_query(self.schema, mquery)
        return  self.querybuilder.build_query(mquery)


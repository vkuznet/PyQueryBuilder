#!/usr/bin/env python

# system modules
from sqlalchemy import sql
#from sqlalchemy import Join
from sqlalchemy.sql.expression import Join

def write_sql_alchemy_graph(dot, metadata, exclude_tables):
    '''This shows how tables relate through foreign keys in a sqlalchemy schema.'''
#    if metadata.name:
#        dot.set_name(metadata.name)
#    else:
#        dot.set_name("A")
    dot.set_name("A")    
    for table_name in metadata.tables:
        if table_name in exclude_tables: 
            continue
        f_keys = metadata.tables[table_name].foreign_keys
        for fk in f_keys:
            right = fk.column.table.name
            if right not in exclude_tables:
                dot.add_edge(table_name, right)
    dot.finish_output()
    

#class MeasureGraph(object):
#    '''This is a writer that just counts the number of edges in a graph.'''
#    def __init__(self):
#        self.name=""
#        self.edgeCnt=0
#        
#    def Name(self,name):
#        self.name=name
#        
#    def AddEdge(self,left,right):
#        self.edgeCnt=self.edgeCnt+1
#
#    def Finish(self):
#        pass
#    
def _write_side(dot, join):
    onclause = join.onclause
    dot.add_edge(onclause.left.table.name, onclause.right.table.name)
    if isinstance(join.left, Join):
        _write_side(dot, join.left)
    if isinstance(join.right, Join):
        _write_side(dot, join.right)

def write_query_alchemy_graph(dot, query):
    '''This writes a sqlalchemy query as a graph showing which tables
    join with which other tables.'''
    dot.set_name("A")
    froms = [xdx for xdx in query.froms]
    if froms:
        _write_side(dot, froms[0])
    dot.finish_output()
   

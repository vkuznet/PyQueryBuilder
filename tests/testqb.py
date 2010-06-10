#!/usr/bin/env python
"""
Test QueryBuilder on Schema object
"""

# system modules
import os

from logging import getLogger
from StringIO import StringIO
from sqlalchemy import select

# local modules
from pyquerybuilder.qb.Schema import Schema, find_table, find_table_name
from pyquerybuilder.qb.Schema import make_view_without_table
from pyquerybuilder.qb.DotGraph import DotGraph
try:
    from UnittestDB import load_from_file, UnittestDB
except :
    pass
from pyquerybuilder.qb.WriteSqlAlchemyGraph import write_query_alchemy_graph
_LOGGER = getLogger("ConstructQuery")


def test_single_query():
    """test create schema from yaml
       get table by name
       create a select query on this table
       create a query builder and build this query"""
    metadata = load_from_file("starting_db.yaml")
    process_dataset = find_table(metadata, 'ProcessedDataset')
    select_test = select([process_dataset.c.Name],
                            process_dataset.c.ID == 0)
    query_builder = Schema(metadata.tables)
    query = query_builder.build_query(select_test)
    print query
def test_operators():
    """test operators"""
    metadata = load_from_file("starting_db.yaml")
    process_dataset = find_table(metadata, 'ProcessedDataset')
    data_tier = find_table(metadata, 'DataTier')
    process_dataset = find_table(metadata, 'PrimaryDataset')
#    files = find_table(metadata,'Files')
    select_test = select([process_dataset.c.Name, data_tier.c.Name,
            process_dataset.c.Description], process_dataset.c.ID==0)
    query_builder = Schema(metadata.tables)
    query = query_builder.build_query(select_test)
    print "query is ", query

test_single_query()
#test_operators()

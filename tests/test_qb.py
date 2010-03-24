#!/usr/bin/env python
"""
Test QueryBuilder on Schema object
"""
import os
from qb.Schema import Schema, find_table, find_table_name
from sqlalchemy import select

from UnittestDB import load_from_file

def test_single_query():
    """test create schema from yaml
       get table by name
       create a select query on this table
       create a query builder and build this query"""
    metadata = load_from_file("starting_db.yaml")
    process_dataset = find_table(metadata, 'ProcessedDataset')
    primary_dataset = find_table(metadata, 'PrimaryDataset')
#    select_test = select([process_dataset.c.Name],
#                            process_dataset.c.ID == 0)
    select_test = select([process_dataset.c.Name, primary_dataset.c.Name],
                            process_dataset.c.ID == 0)
    print "###", select_test
    query_builder = Schema(metadata.tables)
    query = query_builder.build_query(select_test)
    print "+++", query

test_single_query()

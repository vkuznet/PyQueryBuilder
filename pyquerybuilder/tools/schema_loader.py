#!/usr/bin/env python
"""
This load schema from yaml/sql.
"""
__author__ = "LIANG Dong <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.1 $"

import re

from sqlalchemy import MetaData, Column, Table, Integer, ForeignKey
from yaml import load as yamlload
from logging import getLogger

_LOGGER = getLogger("ConstructQuery")

def load_from_file(filename):
    """load from .yaml file or .sql file"""
    suffix = filename.split('.')[-1]
    loader = SchemaLoader()
    if suffix == 'yaml':
        return loader.load_from_file(filename)
    if suffix == 'sql':
        return loader.read_from_oracle(filename)

class SchemaLoader(object):
    """load schema from file"""
    def __init__(self):
        """ initialize"""
        self._metadata = None
        self.ma_table = re.compile("CREATE TABLE (\w+)")
        self.ma_column = re.compile("\s+(\w+)\s+(.*),")
        self.ma_constraint = re.compile("ALTER TABLE\s+(\w+)\s+ADD CONSTRAINT")
        self.ma_foreign = re.compile("key\((\w+)\)\s+references\s+(\w+)\(ID\)")

    def create_from(self, d_input):
        """create from input"""
#        metadata = ThreadLocalMetaData()
        # ThreadLocal don't have a engine
        metadata = MetaData()

        for d_tablename in d_input.keys():
            d_table = d_input[d_tablename]
            s_col = []
            s_vals = {}
            for d_col in d_table:
                d_colname = d_col['member']
                _LOGGER.debug("UnittestDB.create_from: adding %s.%s."
                               % (d_tablename, d_colname))
                if d_col.has_key('foreignKey'):
                    s_col.append(Column(d_colname, Integer,
                                 ForeignKey(d_col["foreignKey"].lower()+".ID")))
                elif d_col.has_key("primaryKey"):
                    s_col.append(Column(d_colname, Integer, primary_key=True))
                else:
                    s_col.append(Column(d_colname, Integer))
                s_vals[d_colname] = 0
            apply(Table, [d_tablename.lower(), metadata] + s_col)
        return metadata

    def load_from_file(self, filename):
        """create metadata from schema file"""
        schema_file = file(filename)
        schema_yaml = yamlload(schema_file)
        schema_file.close()
        metadata = self.create_from(schema_yaml)
        return metadata

    def read_from_oracle(self, filename = "oracle.sql"):
        """read from oracle"""
#        metadata = ThreadLocalMetaData()
        metadata = MetaData()

        file_local = file(filename, "r")
        line = file_local.readline()



        _begin = 0
        _create = 1
        _constraint = 2
        # tables [table_name] = table_name
        tables = {}
        # f_keys [table_name] = (fkey col, ref table_name)
        f_keys = {}
        state = _begin
        while line:
            if state is _begin:
                table_match = self.ma_table.match(line)
                constraint_match = self.ma_constraint.match(line)
                if table_match:
                    current_table = table_match.group(1)
                    tables[current_table] = []
                    f_keys[current_table] = {}
                    state = _create
                elif constraint_match:
                    current_table = constraint_match.group(1)
                    state = _constraint
            elif state is _create:
                col_match = self.ma_column.match(line)
                if line.find(";") > 0:
                    state = _begin
                elif col_match:
                    col = col_match.group(1)
                    if not col == "primary":
                        tables[current_table].append(col)
            elif state is _constraint:
                foreign_match = self.ma_foreign.search(line)
                if foreign_match:
                    l_col = foreign_match.group(1)
                    right_table = foreign_match.group(2)
                    f_keys[current_table][l_col] = right_table
                state = _begin
            line = file_local.readline()
        file_local.close()

        for t_name in tables:
            cols = []
            for col in tables[t_name]:
                if col == "ID":
                    cols.append(Column(col, Integer, primary_key = True))
                elif f_keys[t_name].has_key(col):
                    right_table = f_keys[t_name][col]
                    cols.append(Column(col, Integer,
                                 ForeignKey(right_table + ".ID")))
                else:
                    cols.append(Column(col, Integer))
            apply(Table, [t_name, metadata] + cols)

        return metadata


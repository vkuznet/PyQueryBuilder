#!/usr/bin/env python
"""
App for testing QueryBuilder
"""


import traceback, time, os
from collections import deque
from logging import getLogger
from optparse import OptionParser

from pyquerybuilder.qb.pyqb import QueryBuilder
from pyquerybuilder.tools.config import readconfig
from pyquerybuilder.db.DBManager import DBManager
from pyquerybuilder.qb.ConfigureLog import configurelog
def main():
    """main"""

#    inputs = """find dataset, file, file.block  where dataset
#               like names and primds.startdate > 20100501 or
#                block.size < 250"""
#    inputs = """find block, file where (dataset like names and
#               primds.startdate > 20100501) or block.size < 250"""
#    inputs = """find dataset, count(file), max(block.size)
#               where dataset like cosmic and (dataset.createdate>2010
#               or (block.size > 200 and file.createdate >
#               2010-01-01 02:30:30 CST) or block.size < 500)"""
#    inputs = """find  file where dataset.createdate > 0
#               or (block.size > 0 and file.createdate > 0)
#               or block.size < 0"""

    app.set_mapper(mapfile)
    app.recognize_schema(DB, alias)
    fn = open('tests/test2.txt')
    queries = fn.readlines()

    t_explain = 0.00000
    t_get_cursor = 0.00000
    t_elasped = 0.00000
    t_prt = 0.0
    count = 0
#    fn2 = open('tests/test.sql', 'w')
#    fn3 = open('tests/test2.txt', 'w')
    for query in queries:
        query = query.rstrip()
        start = time.time()
        mquery = app.build_query(query)
        end = time.time()
        cursor1 = time.time()
        res = DB.execute(mquery, alias)
        cursor2 = time.time()
        prt1 = time.time()
        DB.print_result(res, mquery)
        prt2 = time.time()
        t_explain = t_explain + end - start
        t_get_cursor = t_get_cursor + cursor2 - cursor1
        t_elasped = t_elasped + cursor2 + end - cursor1 - start
        t_prt += prt2 - prt1
        count += 1
#            fn3.write(query + '\n')
#            fn2.write(str(mquery)+';\n')
#    fn.close()
#    fn2.close()
    print count
    print t_explain
    print t_get_cursor
    print t_elasped
    print t_prt

    t_total = 0.0
    fn4 = open('tests/test.sql')
    queries = fn4.readlines()
    for query in queries:
        cmd = """/data/mysql/bin/mysql -h liangd.ihep.ac.cn -P 3316 -udbs -pcmsdbs -D CMS_DBS -e '"""
        cmd += query + "'"
        st = time.time()
        os.system(cmd)
        ed = time.time()
        t_total += ed - st

    print t_total
if __name__ == '__main__':
    main()

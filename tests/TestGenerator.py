#!/usr/bin/env python
# $Id: UnittestDB_oracle.py,v 1.1 2007/03/22 15:15:04 valya Exp $
"""
This creates a database for unit tests.
"""
__author__ = "LIANG Dong <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.1 $"

#type : oracle
#account : liangd
#password : tiger
#host : localhost.localdomain
#port : 1522
#database : orcl
#dbowner : liangd
# oracle://liangd:tiger@localhost.localdomain:1522/orcl:liangd
# mysql://cms:passcms@localhost:3306/test
# postgresql://liangd:tiger@localhost:5432/test
# sqlite:///test.db

import re

_DICT = {}

def get_connect_string():
    """get db connect string"""
    cfg_file = open('TestDB.cfg')
    connect_string = ""
    migrate_string = ""

    for cfg_line in cfg_file.readlines():
        if not cfg_line.startswith('#'):
            params = cfg_line.split()
            if len(params) >= 3:
                _DICT[params[0]] = params[2].lower()
            elif len(params) >= 1:
                _DICT[params[0]] = None
    cfg_file.close()          
    
    if _DICT.has_key('type'):
        mtype = _DICT['type']
        if mtype == 'oracle':
            connect_string = "oracle://%s:%s@%s:%s/%s:%s" % \
            (_DICT['account'], _DICT['password'], _DICT['host'], \
             _DICT['port'], _DICT['database'],_DICT['dbowner'])
        elif mtype == 'postgresql' or mtype == 'mysql':
            connect_string = "%s://%s:%s@%s:%s/%s" % \
            (_DICT['type'], _DICT['account'], _DICT['password'], \
             _DICT['host'],  _DICT['port'], _DICT['database'])
        elif _DICT['type'].lower() == 'sqlite':
            connect_string = "sqlite://%s" % _DICT['database']
    else: 
        print "type error"
    if _DICT.has_key('mdatabase') :
        if mtype == 'oracle':
            migrate_string = "oracle://%s:%s@%s:%s/%s:%s" % \
            (_DICT['maccount'], _DICT['mpassword'], _DICT['mhost'], \
             _DICT['mport'], _DICT['mdatabase'],_DICT['mdbowner'])
        elif mtype == 'postgresql' or mtype == 'mysql':
            migrate_string = "%s://%s:%s@%s:%s/%s" % \
            (_DICT['type'], _DICT['maccount'], _DICT['mpassword'], \
             _DICT['mhost'],  _DICT['mport'], _DICT['mdatabase'])
        elif _DICT['type'].lower() == 'sqlite':
            migrate_string = "sqlite://%s" % _DICT['mdatabase']
    return connect_string, migrate_string

def gen_dbmanager_test(connect_string, migrate_string ):
    """generate DBManager test script
        __URL__
        __MURL__
        __PNAME__
        __NAME__
        __MNAME__ """
    template = open('TestDBManager.tpl')
    temp = template.read()
    template.close()
    url = re.compile('__URL__')
    murl = re.compile('__MURL__')
    pname = re.compile('__PNAME__')
    name = re.compile('__NAME__')
    mname = re.compile('__MNAME__')

#   'oracle-orcl-liangd |\#> '
#   'mysql-test-localhost |\#> '
#   'postgresql-test-localhost |\#> '
#   'sqlite-test.db |\#> '
    if _DICT['type'] == 'oracle':
        pname_r = "oracle-%s-%s |\#> " % (_DICT['database'], _DICT['dbowner']) 
        name_r = "oracle-%s-%s" % (_DICT['database'], _DICT['dbowner'])
        mname_r = "oracle-%s-%s" % (_DICT['mdatabase'], _DICT['mdbowner'])

    elif _DICT['type'] == 'sqlite' :
        f_name = _DICT['database'].split("/")[-1]
        pname_r = "sqlite-%s |\#> " % f_name
#        name_r = "%s-sqlite" % f_name
        name_r = "sqlite-%s" % f_name
        f_mname = _DICT['mdatabase'].split("/")[-1]
#        mname_r = "%s-sqlite" % f_mname 
        mname_r = "sqlite-%s" % f_mname
    else: 
        pname_r = "%s-%s-%s |\#> " % (_DICT['type'], _DICT['database'], \
               _DICT['host'])
#        name_r = "%s-%s" % (_DICT['database'], _DICT['type'])
#        mname_r = "%s-%s" % (_DICT['mdatabase'], _DICT['type'])
        name_r = "%s-%s-%s" % (_DICT['type'], _DICT['database'], \
               _DICT['host'])
        mname_r = "%s-%s-%s" % (_DICT['type'], _DICT['mdatabase'], \
               _DICT['mhost'])
               

    temp = url.sub(connect_string, temp)
    temp =  murl.sub(migrate_string, temp)
    temp = pname.sub(pname_r, temp)
    temp = name.sub(name_r, temp)
    temp = mname.sub(mname_r, temp)
#    filename = "TestDBManager_%s.py" % _DICT['type']
    filename = "TestDBManager.py"
    ofile = open(filename,'w')
    ofile.write(temp)
    ofile.close()


    print pname_r, name_r, mname_r

def gen_unittestdb_test(connect_string):
    """generate UnittestDB test"""
    template = open('UnittestDB.tpl')
    temp = template.read()
    template.close()
    url = re.compile('__URL__')
    if _DICT['type'] == 'oracle':
        connect_string = "oracle://%s:%s@%s:%s/%s" % \
            (_DICT['account'], _DICT['password'], _DICT['host'], \
             _DICT['port'], _DICT['database'])
    elif _DICT['type'] == 'sqlite':
        connect_string = "sqlite:///%s" % _DICT['database']

    temp = url.sub(connect_string, temp)
#    filename = "TestDB_%s.py" % _DICT['type']
    filename = "TestDB.py"
    ofile = open(filename,'w')
    ofile.write(temp)
    ofile.close()




if __name__ == '__main__' :
    C_STRING, M_STRING = get_connect_string()
    gen_dbmanager_test(C_STRING, M_STRING)
    gen_unittestdb_test(C_STRING)

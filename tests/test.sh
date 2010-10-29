#!/bin/bash
filename=$0
directory=`dirname $filename`
cd ${directory}
#result=`grep '^type' TestDB.cfg|sed 's/.*:[ ]*//g'` ;
#if [ $result == "sqlite" ]; then
#    `sh test_sqlite.sh`;
#fi
python TestGenerator.py
python test.py

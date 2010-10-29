######################################################
To perfrom all unittests:
   $> sh test.sh 
The default DB-backend is SQLite3
######################################################
To change to other DB-backend (Oracle/MySQL/PostgreSQL), you can follow 
this steps:

1. Create two test DB accounts, one of tem for migration test.
2. Modify TestDB.cfg according to your accounts
3. $> sh test.sh

#######################################################
Here is a short list of current test:
#######################################################
TestGenerator.py
     generate TestDB.py and TestDBManager.py scripts according to TestDB.cfg
TestDB.py
     generate more test schema and fill datas at test database, 
     schema can load from yaml/sql
TestDBManager.py 
     test db manager with database test
     connect/execute sql/desc schema/migrate/drop/
TestGraph.py
     test Graph object
TestConstructQuery.py 
     test ConstuctQuery object using Graph
TestQueryBuilder.py
     test QueryBuilder on Schema object
TestParser.py
     test PLY parser
TestMapper.py
     test mapper function

PyQB Operation
==============

.. toctree::
   :maxdepth: 2

Installation
------------
After verify the dependencies are already installed.

.. doctest::

    $> cd /<path>/QueryBuilder
    $> python setup.py install

Unittest
--------
For PyQB is designed to support different DB backends, unittest are
needed for each DB backend. For test a DB backend, two databases
instance is needed, and there is a configuration file to specify these
two url for testing, **tests/TestDB.cfg**:

.. doctest::

   # type: <DataSource TYPE: oracle postgresql mysql sqlite ...>
   # account : <UserAccount> 
   # password : <Password> 
   # host : <DataSource host>
   # port : <DataSource Port>
   # database : <DataBase name> 
   # dbowner : <DataBase Schema onwer>  
   
   # maccount : <UserAccount for Migrate DB>
   # mpassword : <Password name for Migrate DB>
   # mdatabase : <DataBase name for Migrate DB>
   # mdbowner : <for Migrate DB> , ORACLE ONLY 
   
   # default sqlite section
   type : sqlite
   account : 
   password : 
   host : 
   port : 
   database : test.db 
   dbowner : 
   ## for migration test
   maccount : 
   mpassword :
   mhost :
   mport :
   mdatabase : migrate.db
   mdbowner :

To run the unittest, there are two ways:

.. doctest::

   $> cd /<path>/PyQueryBuilder/tests/
   $> sh test.sh

or 

.. doctest::

   $> cd /<path>/PyQueryBuilder/
   $> python setup.py test

There is a query generator tools to do validation for QL component.
It can generate
 - all single entity queries without constraints
 - all single entity queries with constraints on one attribute
 - all double entities queries with constraints on one attribute

.. doctest::

   $ python tests/TestQueryGenerator.py  -h
   Usage: TestQueryGenerator.py -m mapfile
      -s databaselink -a alias_mapfile

   Options:
     --version             show program's version number and exit
     -h, --help            show this help message and exit
     -m MAPFILE, --mapfile=MAPFILE
                           input registration yaml map file
     -s SOURCE, --source=SOURCE
                           input validate database source link
     -a ALIAS_MAPFILE, --alias_mapfile=ALIAS_MAPFILE
                           input mapfile based on aliased table

Publish a database
------------------
To publish a database a configuration file is need to map between
keywords and table/columns, see :ref:`PyQB Mapper <pyqb_mapping>`.

We provide a appliance to help user review the database schema, see
:ref:`PyQB Schema Viewer <pyqb_schemaviewer>`.

PyQB Server Configuration
-------------------------
PyQB Server configuration consists of a single file: **$PYQB_ROOT/etc/main.cfg**
it's structure is as following example.

.. doctest::

   [server]
   verbose = 0
   server_port = 8310

   environment = production
   profiler = 0
   thread_pool = 30
   socket_queue_size = 15
   expires = 300
   log_screen = True
   access_log_file = /tmp/access_log.log
   error_log_file = /tmp/error_log.log
   error_log_level = 0
   access_log_level = 0

   db_url = mysql://dbs:cmsdbs@liangd.ihep.ac.cn:3316/CMS_DBS
   map_file = etc/map.yaml
   alias_mapfile = etc/map2.yaml
   split_file = etc/split.yaml
   logconfig = etc/logging.conf
   algo = MIS

* **verbose** verbosity level, lowest is 0
* **db_url** database url, replace with your database one.
* **map_file** entity to table.column mapping
* **alias_mapfile** further mapping based on entity mapping
* **split_file** splition for semantic ambiguous erasing
* **algo** algorithm for join table on the fly
   - **MIS** multiple iterator search
   - **LWS** least weight spanning tree search 

.. doctest::

   driver://user:passwd@host:port             # for Mysql
   driver://user:passwd@host:port:db_owner    # for oracle

Running PyQB server
-------------------

Commandline tools:

.. doctest::
    
    $> cd /<path>/QueryBuilder
    $> export QB_ROOT=$PWD
    $> dbsh

WebServer:

.. doctest::

    $> cd /<path>/QueryBuilder
    $> export QB_ROOT=$PWD
    $> python pyquerybuilder/web/web_server.py


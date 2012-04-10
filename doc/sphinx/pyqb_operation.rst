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


PyQB Operation
==============

.. toctree::
   :maxdepth: 2

Installation
------------
After verify the dependencies are already installed.

.. doctest::

   cd PyQueryBuilder
   python setup.py install

Publish a database
------------------
To publish a database a configuration file is need to map between
keywords and table/columns, see :ref:`PyQB Mapper <pyqb_mapping>`.

We provide a appliance to help user review the database schema.

PyQB Server Configuration
-------------------------
PyQB configuration consists of a single file: *$PYQB_ROOT/etc/main.cfg*
it's structure is as following example.

.. doctest::

   [server]
   verbose = 0                                # verbosity level, lowest is 0 
   server_port = 8310                         # web server port 
   logdir = /tmp                              # log file directory
   db_url = tests/test.db                     # database URL 
   map_file = pyquerybuilder/config/map.yaml  # schema mapping file


replace db_url with the your database one.

.. doctest::

   driver://user:passwd@host:port             # for Mysql 
   driver://user:passwd@host:port:db_owner    # for oracle

Running PyQB server
-------------------

Commandline tools:

.. doctest::

    $> sh pyquerybuilder/dbsh.sh 

WebServer:

.. doctest::

    $> python pyquerybuilder/web/web_server.py




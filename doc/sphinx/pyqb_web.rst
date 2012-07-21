PyQB Web Server
===============

.. _pyqb_web:

PyQB web Interface provide two kinds of support for QL queries:
  - a google style query page and display the results in a dynamic table.
  - [JSON]_ api (when results is too big redirect to a stream JSON API)

It is a combination of [CherryPy]_ server, [Cheetah]_ templates, and [YUI]_ data table.

Query Page
----------
http://hostname:port/

JSON API
--------
http://hostname:port/jsonresults?input=QL
http://hostname:port/jsonresults?chunk_size=size&input=QL

chunk_size is optional, value should be in [0, 500000]. default value is 3000.

Streamed JSON API
-----------------
http://hostname:port/stream?chunk_size=size&input=QL
http://hostname:port/stream?input=QL

.. doctest::

   The stream looked like this:

    <json-obj1>\n
    <json-obj2>\n
    ...
    <json-objN>\n

At client side handle simply by

.. doctest::

    a = data.readline()
    while a:
        result = json.loads(a)
        a = data.readline()

Profiler
--------

To enable Cprofile on cherrypy server, set **profiler=1** in **etc/main.cfg**

And the profile file will be generated per api under **/tmp/** directory named as **profile.out.API__N**

[Gprof2Dot]_ is included in to generate Figures in **png** format. This tool need graphviz support.

.. doctest::

   sh $QB_ROOT/pyquerybuilder/tools/profile_graph.sh

it will generate **png** output for profile logs.

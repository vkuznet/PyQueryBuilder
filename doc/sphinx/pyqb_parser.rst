PyQB Parser
===========

Parser is written with the complier tool [PLY]_ .
It accepts QL query, and parse it into a query object.
This query object has explict keywords and constraints information.

.. doctest::

   find count(file.size), file.name where file = /a/b/c#d*               

will be parsed as:

.. doctest::
           
   {'keywords'   : [ ['file.size', 'count'], 
                     ['file.name']], 
    'constraints': [ {'value': '/a/b/c#d*', 
                      'keyword': ['file'], 
                      'sign': '='}]}


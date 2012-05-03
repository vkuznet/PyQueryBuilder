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

And it will support bracket operation.

.. doctest::

   find table where (a >1 and b <2) and (a>3 or d <4)

will be parsed as:

.. doctest::

   {'keywords'   : [ ['table'] ],
    'constraints': [
                     [ {'value': '1', 'keyword': ['a'], 'sign': '>'},
                       'and',
                       {'value': '2', 'keyword': ['b'], 'sign': '<'}],
                     'and', 
                     [ {'value': '3', 'keyword': ['a'], 'sign': '>'},
                       'or',
                       {'value': '4', 'keyword': ['d'], 'sign': '<'}
                     ]
                   ]
   }


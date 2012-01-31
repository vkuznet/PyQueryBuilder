PyQB Mapper
===========
.. _pyqb_mapping:
The Mapper is a function provides mapping from keywords to table/columns.

The dictionary load from a configuration file in [YAML]_ format.

.. doctest::

   file.name : Files.LogicalFileName
   file.size : Files.FileSize
   file.id : Files.ID
   file.checksum : Files.Checksum
   file.numevents : Files.NumberOfEvents
   file.createdate : Files.CreationDate
   file.moddate : Files.LastModificationDate

   tier.name : DataTier.Name
   tier.moddate : DataTier.LastModificationDate
   tier.createdate : DataTier.CreationDate
   ...

Therefore a query such as:

.. doctest::

    {'keywords'   : [ ['file.size', 'count'],
                      ['file.name']],
     'constraints': [ {'value': '/a/b/c#d*',
                       'keyword': ['file'],
                       'sign': '='}]}

will be mapped into

.. doctest::

    {'keywords'   : [ ['Files.FileSize', 'count'],
                      ['Files.LogicalFilename']],
     'constraints': [ {'value': '/a/b/c#d*',
                       'keyword': ['File.LogicalFilename'],
                       'sign': '='}]}



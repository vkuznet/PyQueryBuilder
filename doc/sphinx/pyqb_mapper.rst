PyQB Mapper
===========
.. _pyqb_mapping:
The Mapper is a function provides mapping from keywords to table/columns.

The dictionary load from a configuration file in [YAML]_ format.

.. doctest::

   file :
     -  name : Files.LogicalFileName
     -  size : Files.FileSize
     -  id : Files.ID
     -  checksum : Files.Checksum
     -  numevents : Files.NumberOfEvents
     -  createdate : Files.CreationDate
     -  moddate : Files.LastModificationDate
     -  createdby : 
            - Person.DistinguishedName
            - attribute : Files.CreatedBy
     -  modby : 
            - Files.ModifiedBy, 
            - attribute : Person.DistinguishedName

   tier :
     -  name : DataTier.Name
     -  moddate : DataTier.LastModificationDate
     -  createdate : DataTier.CreationDate
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



PyQB Mapper
===========

.. _pyqb_mapping:

The Mapper is a function provides mapping from keywords to table/columns.

The dictionary load from a configuration file in [YAML]_ format.

basic mapping
-------------

.. doctest::

   file :
     -  name : Files.LogicalFileName
     -  size : Files.FileSize
     -  id : Files.ID
     -  checksum : Files.Checksum
     -  numevents : Files.NumberOfEvents
     -  createdate : Files.CreationDate
     -  moddate : Files.LastModificationDate
     -  createdby : Person.DistinguishedName
     -  modby : Person.DistinguishedName

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
                       'keyword': ['File.LogicalFilename', 'file'],
                       'sign': '='}]}

alias mapping
-------------

With **basic mapping** , we could erase the cycles by creating alias
tables. Then further mapping is possible to specify **parentage attribute**.
see ref:
Alias table is named by Table_Column(see schema_viewer for the Table
name on graph), and is available to be reviewed by
:ref:`PyQB Schema Viewer <pyqb_schemaviewer>`

.. doctest::

   dataset :
     - parent : ProcessedDataset_ItsParent.Name
     - child : ProcessedDataset_ThisDataset.Name

   block :
     - parent : Block_ItsParent.Name
     - child : Block_ThisBlock.Name

   file :
     - parent : Files_ItsParent.LogicalFileName
     - child : Files_ThisFile.LogicalFileName

Graph Splition
--------------

With **mapping** information, still it's possible that exiting semantic ambiguous.
A practical approach is performing splition on schema graph, see ref:

.. doctest::

   ---
   - ProcessedDataset
   - ProcDSRuns
   - Files
   - Block
   - Runs
   - LumiSection
   - FileRunLumi
   ---
   - AnalysisDataset
   - ProcADSParent
   - AnalysisDSFileLumi
   ---
   - AlgorithmConfig
   - FileAlgo
   - ProcAlgo
   ---
   - FileProcQuality
   ---
   - PhysicsGroup
   ---
   - RunLumiQuality
   - QualityHistory
   ---
   - RunLumiDQInt
   - IntQualityHistory
   ...

Mapper Validation tool
----------------------

The mapping infomation could be validate via tool map_reader.py

.. doctest::

   >$ python pyquerybuilder/tools/map_reader.py  -s oracle://account:passwd@orcl:dbname -m etc/map.yaml -v -h
   Usage: map_reader.py -m mapfile
         -v --validate_mapfile=<mapfile> --source=<database link>
         --find_key=<table|table.column> --find_column=<key>
         --find_table=<key> --list_key --list_column --list_entity

   Options:
     --version             show program's version number and exit
     -h, --help            show this help message and exit
     -m MAPFILE, --mapfile=MAPFILE
                           input registration yaml map file
     -v, --validate        perform validation for the mapping
     -f VMAPFILE, --validate_mapfile=VMAPFILE
                           input validate mapfile
     -s SOURCE, --source=SOURCE
                           input validate database source link
     -k FIND_KEY, --find_key=FIND_KEY
                           input table/column to get corresponding key
     -c FIND_COLUMN, --find_column=FIND_COLUMN
                           input key to get table[.column]
     -t FIND_TABLE, --find_table=FIND_TABLE
                           input key to get only table name
     -e, --list_key        list all keys
     -o, --list_column     list all tables/columns
     -i, --list_entity     list all entity

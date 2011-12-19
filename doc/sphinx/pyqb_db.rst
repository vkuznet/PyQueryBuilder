PyQB DBManager
==============

DBManager provides the communication with Database. There are three
major tasks:
   - Load database schema information
   - Execute SQL query
   - Return results

Load schema
-----------
   - load table names
      - oracle  
         - *SELECT table_name FROM all_tables WHERE owner='%s'*
         - *SELECT view_name FROM all_views WHERE owner='%s'*
      - others
         - load by sqlalchemy engine 
   - load table as sqlalchemy object by table_name
   - foreign key links are attached in table objects.


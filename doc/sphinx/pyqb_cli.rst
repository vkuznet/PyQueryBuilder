PyQB CLI tools
=================

PyQB Command Line Interface(CLI) tool provides a interactive shell for 
execute PyQB QL query and other DB operation on database.
It sources from [dbsh]_ project, which is an interactive 
shell for DB back-end. 

Original [dbsh]_ aims to achieve a common, interactive, programmable environment and simple
shell to connect and manipulate your favorite DB content.

Every known DB has its own shell for SQL operations. The dbshell (dbsh)
provides unique, interactive, programmable environment and simple shell
to connect and manipulate your favorite DB contexts. It supports
naturally a syntax of DB you use to, for example, while you connect to
MySQL dbsh supports full syntax of MySQL, but when you connect to ORACLE
it supports ORALCE SQL and commands.

It is based on two components: 
   - interactive python [IPython]_
   - [SQLAlchemy]_

It uses SQLAlchemy ORB tool as an SQL layer to perform interactive
operations against given DB-backend. Therefore it provides common shell
for ANY DB back-end in uniform fashion. All SQL operations supported by
given DB back-end naturally supported by dbsh.

Merged into PyQB project, it supports keyword search ability vis PyQB QL
format.

.. doctest::
    
    [liangd@localhost:doc]$ dbsh
    Welcome to dbsh pydbquery_version!
    [python 2.6.4 (r264:75706, Jan 22 2010, 10:55:09) , ipython 0.10]
    #1 SMP Tue Sep 29 18:45:10 EDT 2009
    For dbsh help use dbhelp, for python help use help commands
    dbsh |1> dbhelp
    Available commands:
    alter      Execute aleter SQL statement
    begin      Execute begin SQL statement
    close      Close connection to DB
    commit     Execute commit SQL statement
    connect    Invoke connection to DB
    create     Execute create SQL statement
    dbhelp     dbsh help
    desc       Print table description
    drop       Execute drop SQL statements
    explain    Execute explain SQL statement
    find       Execute QL expressions
    format     Set-up formatting output
    insert     Execute insert SQL statement
    mapfile    show and set mapfile
    migrate    Migrate content of current DB into another one
    mydb       List all known (connected) DBs
    next       print next set of results
    page       Set pagination
    plot       Produce plot of favorite SQL
    prev       print previous set of results
    rerun      Re-run command
    rollback   Execute rollback SQL statement
    schema     Schema manipulation command
    schemafile show and set schemafile
    select     Execute select SQL statement
    set        Execute set SQL statement
    show       Show information about DB, e.g. show tables
    source     Execute SQL from external file
    update     Execute update SQL statement
    dbsh |1> find help
    
    find: execute <QL expression> 
    QueryLanguage is similar in syntax to SQL (Structured Query Language)
    for 
    databases but is much simpler than SQL. It hides all the complexity of
    SQL 
    but provides the same flexibility. User just need to be concerned about 
    what they want to search and what is the criteria for searching. 
    Here is the basic usage
    
    
       find keywords where constraints ;
    
       keywords is the combination of one or many 'entity' | 'entity.attr' 
                seperated by ','
       constraints is a expression which consist of one of more unit
    expression 
                'keyword ops value' joined with logical operation AND|OR 
       ops are comparable operations: like > < >= <= 

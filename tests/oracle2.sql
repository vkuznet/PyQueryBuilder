CREATE TABLE Person
  (
    ID                    integer,
    Name                  varchar(100),
    DistinguishedName     varchar(500)                                                      unique not null,
    ContactInfo           varchar(250),
    CreationDate          TIMESTAMP DEFAULT SYSTIMESTAMP,
    CreatedBy             integer,
    LastModificationDate  TIMESTAMP DEFAULT SYSTIMESTAMP,
    LastModifiedBy        integer,
    primary key(ID)
  );

REM ======================================================================

ALTER TABLE Person ADD CONSTRAINT
    Person_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
/
ALTER TABLE Person ADD CONSTRAINT
    Person_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
/



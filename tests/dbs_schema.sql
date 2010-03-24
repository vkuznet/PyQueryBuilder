-- ======================================================================
-- ===   Sql Script for Database : DBS_NEW_ERA
-- ===
-- === Build : 756
-- ======================================================================

drop database if exists test;
create database test;
use test;

-- ======================================================================

CREATE TABLE Person
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(100),
    DistinguishedName     varchar(500)    not null,
    ContactInfo           varchar(250),
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique (DistinguishedName(500))
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE Role
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    RoleName              varchar(100)      unique not null,
    RoleDescription       varchar(500)      not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AssignedRole
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    PersonID              BIGINT UNSIGNED   not null,
    RoleID                BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE PhysicsGroup
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    PhysicsGroupName      varchar(500)      unique not null,
    PhysicsGroupConvener  BIGINT UNSIGNED,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE SchemaVersion
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    SchemaVersion         varchar(100)      unique not null,
    InstanceName          varchar(100)      unique not null,
    InstanceType          varchar(10)       unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    DBS_RELEASE_VERSION  varchar(100),
    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE PrimaryDataset
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(100)      unique not null,
    Annotation            varchar(1000)     not null,
    Description           BIGINT UNSIGNED,
    StartDate             varchar(100),
    EndDate               varchar(100),
    Type                  BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcessedDataset
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      not null,
    PrimaryDataset        BIGINT UNSIGNED   not null,
    DataTier              BIGINT UNSIGNED   not null,
    PhysicsGroup          BIGINT UNSIGNED   not null,
    Status                BIGINT UNSIGNED   not null,
    AquisitionEra	  varchar(255),
    GlobalTag             varchar(255),
    XtCrossSection        float,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    DESCRIPTION           varchar(1000),

    primary key(ID),
    unique(Name,PrimaryDataset, DataTier)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE Runs
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    RunNumber             BIGINT UNSIGNED   unique not null,
    NumberOfEvents        BIGINT UNSIGNED   not null,
    NumberOfLumiSections  BIGINT UNSIGNED   not null,
    TotalLuminosity       BIGINT UNSIGNED   not null,
    StoreNumber           BIGINT UNSIGNED   not null,
    StartOfRun            BIGINT,
    EndOfRun              BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE Files
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    LogicalFileName       varchar(500)      unique not null,
    Dataset               BIGINT UNSIGNED   not null,
    Block                 BIGINT UNSIGNED   not null,
    Checksum              varchar(100)      not null,
    Adler32               varchar(100)      default 'NOTSET',
    MD5                   varchar(100)      default 'NOTSET',
    NumberOfEvents        BIGINT UNSIGNED   not null,
    FileSize              BIGINT UNSIGNED   not null,
    FileStatus            BIGINT UNSIGNED   not null,
    FileType              BIGINT UNSIGNED   not null,
    FileBranch            BIGINT UNSIGNED,
    ValidationStatus      BIGINT UNSIGNED,
    QueryableMetadata     varchar(1000)     default 'NOTSET',
    AutoCrossSection      float,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE DataTier
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(100)      unique not null,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE LumiSection
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    LumiSectionNumber     BIGINT UNSIGNED   not null,
    RunNumber             BIGINT UNSIGNED   not null,
    StartEventNumber      BIGINT UNSIGNED   not null,
    EndEventNumber        BIGINT UNSIGNED   not null,
    LumiStartTime         BIGINT,
    LumiEndTime           BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(LumiSectionNumber,RunNumber)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE TimeLog
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Action                varchar(500)      not null,
    Cause                 varchar(500)      not null,
    Effect                varchar(500)      not null,
    Description           varchar(1000)     not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ReasonCode
  (
    ReasonCode            BIGINT UNSIGNED   not null,
    Description           varchar(1000)     not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ReasonCode)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE RecycleBin
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Path                  varchar(500)      not null,
    BlockName             varchar(700)      not null,
    Xml                   LONGTEXT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AlgorithmConfig
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ExecutableName        BIGINT UNSIGNED   not null,
    ApplicationVersion    BIGINT UNSIGNED   not null,
    ApplicationFamily     BIGINT UNSIGNED   not null,
    ParameterSetID        BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(ExecutableName,ApplicationVersion,ApplicationFamily,ParameterSetID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AppFamily
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    FamilyName            varchar(100)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AppVersion
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Version               varchar(100)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AppExecutable
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ExecutableName        varchar(100)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE QueryableParameterSet
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Hash                  varchar(700)      unique not null,
    Name                  varchar(1000),
    Version               varchar(100),
    Type                  varchar(100),
    Annotation            varchar(1000),
    Content               LONGTEXT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ParameterBinding
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Self                  BIGINT UNSIGNED   not null,
    Contains              BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE PrimaryDatasetDescription
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    TriggerDescriptionID    BIGINT UNSIGNED,
    MCChannelDescriptionID  BIGINT UNSIGNED,
    OtherDescriptionID      BIGINT UNSIGNED,
    CreatedBy               BIGINT UNSIGNED,
    CreationDate            BIGINT,
    LastModifiedBy          BIGINT UNSIGNED,
    LastModificationDate    BIGINT,

    primary key(ID),
    unique(TriggerDescriptionID,MCChannelDescriptionID,OtherDescriptionID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE TriggerPathDescription
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    TriggerPathDescription  varchar(100)      unique not null,
    CreatedBy               BIGINT UNSIGNED,
    CreationDate            BIGINT,
    LastModifiedBy          BIGINT UNSIGNED,
    LastModificationDate    BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE MCDescription
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    MCChannelDescription  varchar(100)      not null,
    MCProduction          varchar(100),
    MCDecayChain          varchar(100),
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(MCChannelDescription,MCProduction,MCDecayChain)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE OtherDescription
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Description           varchar(100)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileParentage
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ThisFile              BIGINT UNSIGNED   not null,
    ItsParent             BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(ThisFile,ItsParent)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileRunLumi
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Fileid                BIGINT UNSIGNED   not null,
    Lumi                  BIGINT UNSIGNED,
    Run                   BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Fileid,Lumi,Run)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileAlgo
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Fileid                BIGINT UNSIGNED,
    Algorithm             BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Fileid,Algorithm)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileStatus
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Status                varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileType
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Type                  varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileValidStatus
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Status                varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileTriggerTag
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Fileid                BIGINT UNSIGNED   not null,
    TriggerTag            varchar(500)      not null,
    NumberOfEvents        BIGINT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Fileid,TriggerTag)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileAssoc
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ThisFile              BIGINT UNSIGNED   not null,
    ItsAssoc              BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(ThisFile,ItsAssoc)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcDSRuns
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Dataset               BIGINT UNSIGNED   not null,
    Run                   BIGINT UNSIGNED   not null,
    Complete 		  BIGINT UNSIGNED   default 0,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Dataset,Run)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcDSParent
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ThisDataset           BIGINT UNSIGNED   not null,
    ItsParent             BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(ThisDataset,ItsParent)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcAlgo
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Dataset               BIGINT UNSIGNED   not null,
    Algorithm             BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Dataset,Algorithm)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcADSParent
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ThisDataset           BIGINT UNSIGNED   not null,
    ItsParentADS          BIGINT UNSIGNED   not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(ThisDataset,ItsParentADS)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AnalysisDataset
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      not null,
    Version               BIGINT            not null,
    Path                  varchar(500)      not null,
    Definition            BIGINT UNSIGNED   not null,
    Description           varchar(1000),
    PhysicsGroup          BIGINT UNSIGNED   not null,
    ProcessedDS           BIGINT UNSIGNED   not null,
    Type                  BIGINT UNSIGNED,
    Status                BIGINT UNSIGNED,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID),
    unique(Name,Version)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AnalysisDSType
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Type                  varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AnalysisDSStatus
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Status                varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AnalysisDSFileLumi
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    AnalysisDataset       BIGINT UNSIGNED   not null,
    Lumi                  BIGINT UNSIGNED,
    Fileid                BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(AnalysisDataset,Lumi,Fileid)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE AnalysisDSDef
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(700)      unique not null,
    Path                  varchar(1000),
    Description           TEXT,
    UserInput             TEXT,
    SQLQuery              TEXT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE CompositeADS
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      unique not null,
    Description           varchar(1000)     not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE CompADSMap
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    CompADS               BIGINT UNSIGNED   not null,
    ADS                   BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(CompADS,ADS)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE SEBlock
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    SEID                  BIGINT UNSIGNED   not null,
    Roles                 char(1)           default 'Y',
    BlockID               BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(SEID,BlockID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE StorageElement
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    SEName                varchar(500)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE Block
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      unique not null,
    Path                  varchar(500)      not null,
    Dataset               BIGINT UNSIGNED   not null,
    BlockSize             BIGINT UNSIGNED   not null,
    NumberOfFiles         BIGINT UNSIGNED   not null,
    NumberOfEvents        BIGINT UNSIGNED   not null,
    OpenForWriting        int               not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE BlockParent
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ThisBlock             BIGINT UNSIGNED not null,
    ItsParent             BIGINT UNSIGNED not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    primary key(ID),
    unique(ThisBlock,ItsParent)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE FileProcQuality
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ParentFile            BIGINT UNSIGNED not null,
    ChildDataset          BIGINT UNSIGNED not null,
    ProcessingStatus      BIGINT UNSIGNED not null,
    FailedEventCount      BIGINT UNSIGNED,
    FailedEventList       varchar(500),
    Description           varchar(1000),
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    primary key(ID),
    unique(ParentFile,ChildDataset)
  )ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcessingStatus
   (
    ID                    BIGINT UNSIGNED not null auto_increment,
    ProcessingStatus      varchar(50),
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    primary key(ID)
   )ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE ProcDSStatus
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Status                varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE PrimaryDSType
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Type                  varchar(100)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE QualityValues
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Value                 varchar(500)      unique not null,
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE SubSystem
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      unique not null,
    Parent                varchar(500)      not null default 'CMS',
    CreatedBy             BIGINT UNSIGNED,
    CreationDate          BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,
    LastModificationDate  BIGINT,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE RunLumiQuality
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Dataset               BIGINT UNSIGNED   not null,
    Run                   BIGINT UNSIGNED   not null,
    Lumi                  BIGINT UNSIGNED,
    SubSystem             BIGINT UNSIGNED   not null,
    DQValue               BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Run,Lumi,SubSystem)
  ) ENGINE = InnoDB ;


-- ======================================================================
    
CREATE TABLE RunLumiDQInt
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Dataset               BIGINT UNSIGNED   not null,
    Run                   BIGINT UNSIGNED   not null,
    Lumi                  BIGINT UNSIGNED,
    SubSystem             BIGINT UNSIGNED   not null,
    IntDQValue            INT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(Run,Lumi,SubSystem)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE QualityHistory
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    HistoryOf             BIGINT UNSIGNED,
    HistoryTimeStamp      BIGINT            not null,
    Dataset               BIGINT UNSIGNED   not null,
    Run                   BIGINT UNSIGNED   not null,
    Lumi                  BIGINT UNSIGNED,
    SubSystem             BIGINT UNSIGNED   not null,
    DQValue               BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(HistoryTimeStamp,Run,Lumi,SubSystem,DQValue)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE IntQualityHistory
  (
    ID                    BIGINT UNSIGNED,
    HistoryOf             BIGINT UNSIGNED,
    HistoryTimeStamp      integer   not null,
    Dataset               BIGINT UNSIGNED not null,
    Run                   BIGINT UNSIGNED not null,
    Lumi                  BIGINT UNSIGNED,
    SubSystem             BIGINT UNSIGNED   not null,
    IntDQValue            integer   not null,
    CreationDate          integer,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  integer,
    LastModifiedBy        BIGINT UNSIGNED,
    primary key(ID),
    unique(HistoryTimeStamp,Run,Lumi,SubSystem, IntDQValue)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE QualityVersion
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Version               varchar(500)      unique not null,
    VersionTimeStamp      BIGINT            unique not null,
    Description           varchar(1000),
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE Branch
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Name                  varchar(500)      unique not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE BranchHash
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    Hash                  varchar(700)      unique not null,
    Description           varchar(1000),
    Content               LONGTEXT,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID)
  ) ENGINE = InnoDB ;

-- ======================================================================

CREATE TABLE BranchHashMap
  (
    ID                    BIGINT UNSIGNED not null auto_increment,
    BranchID              BIGINT UNSIGNED   not null,
    BranchHashID          BIGINT UNSIGNED   not null,
    CreationDate          BIGINT,
    CreatedBy             BIGINT UNSIGNED,
    LastModificationDate  BIGINT,
    LastModifiedBy        BIGINT UNSIGNED,

    primary key(ID),
    unique(BranchID,BranchHashID)
  ) ENGINE = InnoDB ;

-- ======================================================================

ALTER TABLE Person ADD CONSTRAINT 
    Person_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Person ADD CONSTRAINT 
    Person_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE Role ADD CONSTRAINT 
    Role_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Role ADD CONSTRAINT 
    Role_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AssignedRole ADD CONSTRAINT 
    AssignedRole_PersonID_FK foreign key(PersonID) references Person(ID)
;
ALTER TABLE AssignedRole ADD CONSTRAINT 
    AssignedRole_RoleID_FK foreign key(RoleID) references Role(ID)
;
ALTER TABLE AssignedRole ADD CONSTRAINT 
    AssignedRole_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AssignedRole ADD CONSTRAINT 
    AssignedRole_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE PhysicsGroup ADD CONSTRAINT 
    PhysicsGroupPhysicsGroupCon_FK foreign key(PhysicsGroupConvener) references Person(ID)
;
ALTER TABLE PhysicsGroup ADD CONSTRAINT 
    PhysicsGroup_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE PhysicsGroup ADD CONSTRAINT 
    PhysicsGroup_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE SchemaVersion ADD CONSTRAINT 
    SchemaVersion_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE SchemaVersion ADD CONSTRAINT 
    SchemaVersionLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE PrimaryDataset ADD CONSTRAINT 
    PrimaryDataset_Description_FK foreign key(Description) references PrimaryDatasetDescription(ID)
;
ALTER TABLE PrimaryDataset ADD CONSTRAINT 
    PrimaryDataset_Type_FK foreign key(Type) references PrimaryDSType(ID)
;
ALTER TABLE PrimaryDataset ADD CONSTRAINT 
    PrimaryDataset_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE PrimaryDataset ADD CONSTRAINT 
    PrimaryDatasetLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcessedDataset ADD CONSTRAINT 
    ProcessedDatasetPrimaryData_FK foreign key(PrimaryDataset) references PrimaryDataset(ID) on delete CASCADE
;
ALTER TABLE ProcessedDataset ADD CONSTRAINT 
    ProcessedDatasetPhysicsGrou_FK foreign key(PhysicsGroup) references PhysicsGroup(ID)
;
ALTER TABLE ProcessedDataset ADD CONSTRAINT 
    ProcessedDataset_Status_FK foreign key(Status) references ProcDSStatus(ID)
;
ALTER TABLE ProcessedDataset ADD CONSTRAINT 
    ProcessedDataset_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcessedDataset ADD CONSTRAINT 
    ProcessedDatasetLastModifie_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcessedDataset ADD CONSTRAINT
    ProcessedDataset_DataTier_FK foreign key(DataTier) references DataTier(ID)
;

ALTER TABLE Runs ADD CONSTRAINT 
    Runs_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Runs ADD CONSTRAINT 
    Runs_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE Files ADD CONSTRAINT 
    Files_Dataset_FK foreign key(Dataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_Block_FK foreign key(Block) references Block(ID) on delete CASCADE
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_FileStatus_FK foreign key(FileStatus) references FileStatus(ID)
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_FileType_FK foreign key(FileType) references FileType(ID)
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_FileBranch_FK foreign key(FileBranch) references BranchHash(ID)
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_ValidationStatus_FK foreign key(ValidationStatus) references FileValidStatus(ID)
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Files ADD CONSTRAINT 
    Files_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE DataTier ADD CONSTRAINT 
    DataTier_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;
ALTER TABLE DataTier ADD CONSTRAINT 
    DataTier_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;

ALTER TABLE LumiSection ADD CONSTRAINT 
    LumiSection_RunNumber_FK foreign key(RunNumber) references Runs(ID)
;
ALTER TABLE LumiSection ADD CONSTRAINT 
    LumiSection_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE LumiSection ADD CONSTRAINT 
    LumiSection_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE TimeLog ADD CONSTRAINT 
    TimeLog_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE TimeLog ADD CONSTRAINT 
    TimeLog_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ReasonCode ADD CONSTRAINT 
    ReasonCode_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ReasonCode ADD CONSTRAINT 
    ReasonCode_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE RecycleBin ADD CONSTRAINT 
    RecycleBin_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE RecycleBin ADD CONSTRAINT 
    RecycleBin_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfigExecutableNa_FK foreign key(ExecutableName) references AppExecutable(ID)
;
ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfigApplicationV_FK foreign key(ApplicationVersion) references AppVersion(ID)
;
ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfigApplicationF_FK foreign key(ApplicationFamily) references AppFamily(ID)
;
ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfigParameterSet_FK foreign key(ParameterSetID) references QueryableParameterSet(ID)
;
ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfig_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AlgorithmConfig ADD CONSTRAINT 
    AlgorithmConfigLastModified_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AppFamily ADD CONSTRAINT 
    AppFamily_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AppFamily ADD CONSTRAINT 
    AppFamily_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AppVersion ADD CONSTRAINT 
    AppVersion_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AppVersion ADD CONSTRAINT 
    AppVersion_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AppExecutable ADD CONSTRAINT 
    AppExecutable_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AppExecutable ADD CONSTRAINT 
    AppExecutableLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE QueryableParameterSet ADD CONSTRAINT 
    QueryableParameterSetCreate_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE QueryableParameterSet ADD CONSTRAINT 
    QueryableParameterSetLastMo_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ParameterBinding ADD CONSTRAINT 
    ParameterBinding_Self_FK foreign key(Self) references QueryableParameterSet(ID)
;
ALTER TABLE ParameterBinding ADD CONSTRAINT 
    ParameterBinding_Contains_FK foreign key(Contains) references QueryableParameterSet(ID)
;
ALTER TABLE ParameterBinding ADD CONSTRAINT 
    ParameterBinding_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ParameterBinding ADD CONSTRAINT 
    ParameterBindingLastModifie_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE PrimaryDatasetDescription ADD CONSTRAINT 
    PrimaryDatasetDescriptionTr_FK foreign key(TriggerDescriptionID) references TriggerPathDescription(ID)
;
ALTER TABLE PrimaryDatasetDescription ADD CONSTRAINT 
    PrimaryDatasetDescriptionMC_FK foreign key(MCChannelDescriptionID) references MCDescription(ID)
;
ALTER TABLE PrimaryDatasetDescription ADD CONSTRAINT 
    PrimaryDatasetDescriptionOt_FK foreign key(OtherDescriptionID) references OtherDescription(ID)
;
ALTER TABLE PrimaryDatasetDescription ADD CONSTRAINT 
    PrimaryDatasetDescriptionCr_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE PrimaryDatasetDescription ADD CONSTRAINT 
    PrimaryDatasetDescriptionLa_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE TriggerPathDescription ADD CONSTRAINT 
    TriggerPathDescriptionCreat_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE TriggerPathDescription ADD CONSTRAINT 
    TriggerPathDescriptionLastM_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE MCDescription ADD CONSTRAINT 
    MCDescription_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE MCDescription ADD CONSTRAINT 
    MCDescriptionLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE OtherDescription ADD CONSTRAINT 
    OtherDescription_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE OtherDescription ADD CONSTRAINT 
    OtherDescriptionLastModifie_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileParentage ADD CONSTRAINT 
    FileParentage_ThisFile_FK foreign key(ThisFile) references Files(ID) on delete CASCADE
;
ALTER TABLE FileParentage ADD CONSTRAINT 
    FileParentage_ItsParent_FK foreign key(ItsParent) references Files(ID) on delete CASCADE
;
ALTER TABLE FileParentage ADD CONSTRAINT 
    FileParentage_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileParentage ADD CONSTRAINT 
    FileParentageLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

-- ALTER TABLE FileRunLumi ADD CONSTRAINT 
--    FileRunLumi_Fileid_FK foreign key(Fileid) references Files(ID) on delete CASCADE
-- ;
-- ALTER TABLE FileRunLumi ADD CONSTRAINT 
--    FileRunLumi_Lumi_FK foreign key(Lumi) references LumiSection(ID)
-- ;
-- ALTER TABLE FileRunLumi ADD CONSTRAINT 
--    FileRunLumi_Run_FK foreign key(Run) references Runs(ID)
-- ;
-- ALTER TABLE FileRunLumi ADD CONSTRAINT 
--    FileRunLumi_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
-- ;
-- ALTER TABLE FileRunLumi ADD CONSTRAINT 
--    FileRunLumi_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
-- ;

ALTER TABLE FileAlgo ADD CONSTRAINT 
    FileAlgo_Fileid_FK foreign key(Fileid) references Files(ID) on delete CASCADE
;
ALTER TABLE FileAlgo ADD CONSTRAINT 
    FileAlgo_Algorithm_FK foreign key(Algorithm) references AlgorithmConfig(ID)
;
ALTER TABLE FileAlgo ADD CONSTRAINT 
    FileAlgo_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileAlgo ADD CONSTRAINT 
    FileAlgo_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileStatus ADD CONSTRAINT 
    FileStatus_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileStatus ADD CONSTRAINT 
    FileStatus_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileType ADD CONSTRAINT 
    FileType_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileType ADD CONSTRAINT 
    FileType_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileValidStatus ADD CONSTRAINT 
    FileValidStatus_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileValidStatus ADD CONSTRAINT 
    FileValidStatusLastModified_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileTriggerTag ADD CONSTRAINT 
    FileTriggerTag_Fileid_FK foreign key(Fileid) references Files(ID) on delete CASCADE
;
ALTER TABLE FileTriggerTag ADD CONSTRAINT 
    FileTriggerTag_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileTriggerTag ADD CONSTRAINT 
    FileTriggerTagLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE FileAssoc ADD CONSTRAINT 
    FileAssoc_ThisFile_FK foreign key(ThisFile) references Files(ID) on delete CASCADE
;
ALTER TABLE FileAssoc ADD CONSTRAINT 
    FileAssoc_ItsAssoc_FK foreign key(ItsAssoc) references Files(ID) on delete CASCADE
;
ALTER TABLE FileAssoc ADD CONSTRAINT 
    FileAssoc_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileAssoc ADD CONSTRAINT 
    FileAssoc_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcDSRuns ADD CONSTRAINT 
    ProcDSRuns_Dataset_FK foreign key(Dataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE ProcDSRuns ADD CONSTRAINT 
    ProcDSRuns_Run_FK foreign key(Run) references Runs(ID)
;
ALTER TABLE ProcDSRuns ADD CONSTRAINT 
    ProcDSRuns_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcDSRuns ADD CONSTRAINT 
    ProcDSRuns_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

--

ALTER TABLE BlockParent ADD CONSTRAINT
    BlockParent_ThisBlock_FK foreign key(ThisBlock) references Block(ID) on delete CASCADE
;   
ALTER TABLE BlockParent ADD CONSTRAINT
    BlockParent_ItsParent_FK foreign key(ItsParent) references Block(ID) on delete CASCADE
;   
ALTER TABLE BlockParent ADD CONSTRAINT
    BlockParent_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;   
ALTER TABLE BlockParent ADD CONSTRAINT
    BlockParentLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

--

ALTER TABLE FileProcQuality ADD CONSTRAINT
    FPQ_ParentFile_FK foreign key(ParentFile) references Files(ID) on delete CASCADE
;
ALTER TABLE FileProcQuality ADD CONSTRAINT
    FPQ_ChildDataset_FK foreign key(ChildDataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE FileProcQuality ADD CONSTRAINT
    FPQ_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE FileProcQuality ADD CONSTRAINT
    FPQLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;
ALTER TABLE FileProcQuality ADD CONSTRAINT
    FPQ_Status_FK foreign key(ProcessingStatus) references ProcessingStatus(ID) on delete CASCADE
;

--

ALTER TABLE ProcessingStatus ADD CONSTRAINT
    ProcStatus_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcessingStatus ADD CONSTRAINT
    ProcStatusLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcDSParent ADD CONSTRAINT 
    ProcDSParent_ThisDataset_FK foreign key(ThisDataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE ProcDSParent ADD CONSTRAINT 
    ProcDSParent_ItsParent_FK foreign key(ItsParent) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE ProcDSParent ADD CONSTRAINT 
    ProcDSParent_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcDSParent ADD CONSTRAINT 
    ProcDSParent_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcAlgo ADD CONSTRAINT 
    ProcAlgo_Dataset_FK foreign key(Dataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE ProcAlgo ADD CONSTRAINT 
    ProcAlgo_Algorithm_FK foreign key(Algorithm) references AlgorithmConfig(ID) on delete CASCADE
;
ALTER TABLE ProcAlgo ADD CONSTRAINT 
    ProcAlgo_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcAlgo ADD CONSTRAINT 
    ProcAlgo_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcADSParent ADD CONSTRAINT 
    ProcADSParent_ThisDataset_FK foreign key(ThisDataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE ProcADSParent ADD CONSTRAINT 
    ProcADSParent_ItsParentADS_FK foreign key(ItsParentADS) references AnalysisDataset(ID) on delete CASCADE
;
ALTER TABLE ProcADSParent ADD CONSTRAINT 
    ProcADSParent_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcADSParent ADD CONSTRAINT 
    ProcADSParentLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDataset_Definition_FK foreign key(Definition) references AnalysisDSDef(ID)
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDatasetPhysicsGroup_FK foreign key(PhysicsGroup) references PhysicsGroup(ID)
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDataset_ProcessedDS_FK foreign key(ProcessedDS) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDataset_Type_FK foreign key(Type) references AnalysisDSType(ID)
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDataset_Status_FK foreign key(Status) references AnalysisDSStatus(ID)
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDataset_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AnalysisDataset ADD CONSTRAINT 
    AnalysisDatasetLastModified_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AnalysisDSType ADD CONSTRAINT 
    AnalysisDSType_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AnalysisDSType ADD CONSTRAINT 
    AnalysisDSTypeLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AnalysisDSStatus ADD CONSTRAINT 
    AnalysisDSStatus_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AnalysisDSStatus ADD CONSTRAINT 
    AnalysisDSStatusLastModifie_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AnalysisDSFileLumi ADD CONSTRAINT 
    AnalysisDSFileLumiAnalysisD_FK foreign key(AnalysisDataset) references AnalysisDataset(ID) on delete CASCADE
;
ALTER TABLE AnalysisDSFileLumi ADD CONSTRAINT 
    AnalysisDSFileLumi_Lumi_FK foreign key(Lumi) references LumiSection(ID)
;
ALTER TABLE AnalysisDSFileLumi ADD CONSTRAINT 
    AnalysisDSFileLumi_Fileid_FK foreign key(Fileid) references Files(ID)
;
ALTER TABLE AnalysisDSFileLumi ADD CONSTRAINT 
    AnalysisDSFileLumiCreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AnalysisDSFileLumi ADD CONSTRAINT 
    AnalysisDSFileLumiLastModif_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE AnalysisDSDef ADD CONSTRAINT 
    AnalysisDSDef_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE AnalysisDSDef ADD CONSTRAINT 
    AnalysisDSDefLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE CompositeADS ADD CONSTRAINT 
    CompositeADS_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE CompositeADS ADD CONSTRAINT 
    CompositeADS_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE CompADSMap ADD CONSTRAINT 
    CompADSMap_CompADS_FK foreign key(CompADS) references CompositeADS(ID)
;
ALTER TABLE CompADSMap ADD CONSTRAINT 
    CompADSMap_ADS_FK foreign key(ADS) references AnalysisDataset(ID) on delete CASCADE
;
ALTER TABLE CompADSMap ADD CONSTRAINT 
    CompADSMap_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE CompADSMap ADD CONSTRAINT 
    CompADSMap_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE SEBlock ADD CONSTRAINT 
    SEBlock_SEID_FK foreign key(SEID) references StorageElement(ID) on delete CASCADE
;
ALTER TABLE SEBlock ADD CONSTRAINT 
    SEBlock_BlockID_FK foreign key(BlockID) references Block(ID) on delete CASCADE
;
ALTER TABLE SEBlock ADD CONSTRAINT 
    SEBlock_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE SEBlock ADD CONSTRAINT 
    SEBlock_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE StorageElement ADD CONSTRAINT 
    StorageElement_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE StorageElement ADD CONSTRAINT 
    StorageElementLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE Block ADD CONSTRAINT 
    Block_Dataset_FK foreign key(Dataset) references ProcessedDataset(ID) on delete CASCADE
;
ALTER TABLE Block ADD CONSTRAINT 
    Block_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Block ADD CONSTRAINT 
    Block_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE ProcDSStatus ADD CONSTRAINT 
    ProcDSStatus_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE ProcDSStatus ADD CONSTRAINT 
    ProcDSStatus_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE PrimaryDSType ADD CONSTRAINT 
    PrimaryDSType_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE PrimaryDSType ADD CONSTRAINT 
    PrimaryDSTypeLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE QualityValues ADD CONSTRAINT 
    QualityValues_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE QualityValues ADD CONSTRAINT 
    QualityValuesLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE SubSystem ADD CONSTRAINT 
    SubSystem_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE SubSystem ADD CONSTRAINT 
    SubSystem_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQuality_Run_FK foreign key(Run) references Runs(ID)
;
ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQuality_Lumi_FK foreign key(Lumi) references LumiSection(ID)
;
ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQuality_SubSystem_FK foreign key(SubSystem) references SubSystem(ID) on delete CASCADE
;
ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQuality_DQValue_FK foreign key(DQValue) references QualityValues(ID) on delete CASCADE
;
ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQuality_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE RunLumiQuality ADD CONSTRAINT 
    RunLumiQualityLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;


ALTER TABLE RunLumiDQInt ADD CONSTRAINT
    RunLumiDQInt_Run_FK foreign key(Run) references Runs(ID)
;
ALTER TABLE RunLumiDQInt ADD CONSTRAINT   
    RunLumiDQInt_Lumi_FK foreign key(Lumi) references LumiSection(ID)
;   
ALTER TABLE RunLumiDQInt ADD CONSTRAINT 
    RunLumiDQInt_SubSystem_FK foreign key(SubSystem) references SubSystem(ID) on delete CASCADE
;
ALTER TABLE RunLumiDQInt ADD CONSTRAINT
    RunLumiDQInt_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE RunLumiDQInt ADD CONSTRAINT
    RunLumiDQIntLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_HistoryOf_FK foreign key(HistoryOf) references RunLumiQuality(ID)
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_Run_FK foreign key(Run) references Runs(ID)
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_Lumi_FK foreign key(Lumi) references LumiSection(ID)
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_SubSystem_FK foreign key(SubSystem) references SubSystem(ID) on delete CASCADE
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_DQValue_FK foreign key(DQValue) references QualityValues(ID) on delete CASCADE
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistory_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE QualityHistory ADD CONSTRAINT 
    QualityHistoryLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;


ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_HistoryOf_FK foreign key(HistoryOf) references RunLumiDQInt(ID)
;
   
ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_Run_FK foreign key(Run) references Runs(ID)
;
   
ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_Dataset_FK foreign key(Dataset) references ProcessedDataset(ID)
;
   
ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_Lumi_FK foreign key(Lumi) references LumiSection(ID)
;
   
ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_SubSystem_FK foreign key(SubSystem) references SubSystem(ID) on delete CASCADE
;
   
ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQualityHistory_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;

ALTER TABLE IntQualityHistory ADD CONSTRAINT
    IntQHistLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
; 


ALTER TABLE QualityVersion ADD CONSTRAINT 
    QualityVersion_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE QualityVersion ADD CONSTRAINT 
    QualityVersionLastModifiedB_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE Branch ADD CONSTRAINT 
    Branch_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE Branch ADD CONSTRAINT 
    Branch_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE BranchHash ADD CONSTRAINT 
    BranchHash_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE BranchHash ADD CONSTRAINT 
    BranchHash_LastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

ALTER TABLE BranchHashMap ADD CONSTRAINT 
    BranchHashMap_BranchID_FK foreign key(BranchID) references Branch(ID) on delete CASCADE
;
ALTER TABLE BranchHashMap ADD CONSTRAINT 
    BranchHashMap_BranchHashID_FK foreign key(BranchHashID) references BranchHash(ID)
;
ALTER TABLE BranchHashMap ADD CONSTRAINT 
    BranchHashMap_CreatedBy_FK foreign key(CreatedBy) references Person(ID)
;
ALTER TABLE BranchHashMap ADD CONSTRAINT 
    BranchHashMapLastModifiedBy_FK foreign key(LastModifiedBy) references Person(ID)
;

-- =========== INSERT TRIGGERS FOR LastModificationDate ============================

CREATE TRIGGER TR_Person BEFORE INSERT ON Person
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_Role BEFORE INSERT ON Role
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AssignedRole BEFORE INSERT ON AssignedRole
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_PhysicsGroup BEFORE INSERT ON PhysicsGroup
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_SchemaVersion BEFORE INSERT ON SchemaVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_PrimaryDataset BEFORE INSERT ON PrimaryDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcessedDataset BEFORE INSERT ON ProcessedDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_Runs BEFORE INSERT ON Runs
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_Files BEFORE INSERT ON Files
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_DataTier BEFORE INSERT ON DataTier
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_LumiSection BEFORE INSERT ON LumiSection
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_TimeLog BEFORE INSERT ON TimeLog
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ReasonCode BEFORE INSERT ON ReasonCode
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_RecycleBin BEFORE INSERT ON RecycleBin
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AlgorithmConfig BEFORE INSERT ON AlgorithmConfig
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AppFamily BEFORE INSERT ON AppFamily
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AppVersion BEFORE INSERT ON AppVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AppExecutable BEFORE INSERT ON AppExecutable
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_QueryableParameterSet BEFORE INSERT ON QueryableParameterSet
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ParameterBinding BEFORE INSERT ON ParameterBinding
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_PrimaryDatasetDescription BEFORE INSERT ON PrimaryDatasetDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_TriggerPathDescription BEFORE INSERT ON TriggerPathDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_MCDescription BEFORE INSERT ON MCDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_OtherDescription BEFORE INSERT ON OtherDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileParentage BEFORE INSERT ON FileParentage
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileRunLumi BEFORE INSERT ON FileRunLumi
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileAlgo BEFORE INSERT ON FileAlgo
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileStatus BEFORE INSERT ON FileStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileType BEFORE INSERT ON FileType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileValidStatus BEFORE INSERT ON FileValidStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileTriggerTag BEFORE INSERT ON FileTriggerTag
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileAssoc BEFORE INSERT ON FileAssoc
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcDSRuns BEFORE INSERT ON ProcDSRuns
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcDSParent BEFORE INSERT ON ProcDSParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcAlgo BEFORE INSERT ON ProcAlgo
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcADSParent BEFORE INSERT ON ProcADSParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AnalysisDataset BEFORE INSERT ON AnalysisDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AnalysisDSType BEFORE INSERT ON AnalysisDSType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AnalysisDSStatus BEFORE INSERT ON AnalysisDSStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AnalysisDSFileLumi BEFORE INSERT ON AnalysisDSFileLumi
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_AnalysisDSDef BEFORE INSERT ON AnalysisDSDef
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_CompositeADS BEFORE INSERT ON CompositeADS
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_CompADSMap BEFORE INSERT ON CompADSMap
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_SEBlock BEFORE INSERT ON SEBlock
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_StorageElement BEFORE INSERT ON StorageElement
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_Block BEFORE INSERT ON Block
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcDSStatus BEFORE INSERT ON ProcDSStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_PrimaryDSType BEFORE INSERT ON PrimaryDSType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_QualityValues BEFORE INSERT ON QualityValues
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_SubSystem BEFORE INSERT ON SubSystem
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_RunLumiQuality BEFORE INSERT ON RunLumiQuality
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_RunLumiDQInt BEFORE INSERT ON RunLumiDQInt
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_QualityVersion BEFORE INSERT ON QualityVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_Branch BEFORE INSERT ON Branch
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_BranchHash BEFORE INSERT ON BranchHash
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_BranchHashMap BEFORE INSERT ON BranchHashMap
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_BlockParent BEFORE INSERT ON BlockParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_FileProcQuality BEFORE INSERT ON FileProcQuality
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER TR_ProcessStatus BEFORE INSERT ON ProcessingStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

-- =========== UPDATE TRIGGERS FOR LastModificationDate ============================

CREATE TRIGGER UTR_Person BEFORE UPDATE ON Person
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_Role BEFORE UPDATE ON Role
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AssignedRole BEFORE UPDATE ON AssignedRole
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_PhysicsGroup BEFORE UPDATE ON PhysicsGroup
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_SchemaVersion BEFORE UPDATE ON SchemaVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_PrimaryDataset BEFORE UPDATE ON PrimaryDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcessedDataset BEFORE UPDATE ON ProcessedDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_Runs BEFORE UPDATE ON Runs
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_Files BEFORE UPDATE ON Files
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_DataTier BEFORE UPDATE ON DataTier
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_LumiSection BEFORE UPDATE ON LumiSection
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_TimeLog BEFORE UPDATE ON TimeLog
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ReasonCode BEFORE UPDATE ON ReasonCode
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_RecycleBin BEFORE UPDATE ON RecycleBin
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AlgorithmConfig BEFORE UPDATE ON AlgorithmConfig
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AppFamily BEFORE UPDATE ON AppFamily
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AppVersion BEFORE UPDATE ON AppVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AppExecutable BEFORE UPDATE ON AppExecutable
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_QueryableParameterSet BEFORE UPDATE ON QueryableParameterSet
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ParameterBinding BEFORE UPDATE ON ParameterBinding
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_PrimaryDatasetDescription BEFORE UPDATE ON PrimaryDatasetDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_TriggerPathDescription BEFORE UPDATE ON TriggerPathDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_MCDescription BEFORE UPDATE ON MCDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_OtherDescription BEFORE UPDATE ON OtherDescription
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileParentage BEFORE UPDATE ON FileParentage
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileRunLumi BEFORE UPDATE ON FileRunLumi
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileAlgo BEFORE UPDATE ON FileAlgo
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileStatus BEFORE UPDATE ON FileStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileType BEFORE UPDATE ON FileType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileValidStatus BEFORE UPDATE ON FileValidStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileTriggerTag BEFORE UPDATE ON FileTriggerTag
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileAssoc BEFORE UPDATE ON FileAssoc
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcDSRuns BEFORE UPDATE ON ProcDSRuns
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcDSParent BEFORE UPDATE ON ProcDSParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcAlgo BEFORE UPDATE ON ProcAlgo
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcADSParent BEFORE UPDATE ON ProcADSParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AnalysisDataset BEFORE UPDATE ON AnalysisDataset
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AnalysisDSType BEFORE UPDATE ON AnalysisDSType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AnalysisDSStatus BEFORE UPDATE ON AnalysisDSStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AnalysisDSFileLumi BEFORE UPDATE ON AnalysisDSFileLumi
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_AnalysisDSDef BEFORE UPDATE ON AnalysisDSDef
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_CompositeADS BEFORE UPDATE ON CompositeADS
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_CompADSMap BEFORE UPDATE ON CompADSMap
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_SEBlock BEFORE UPDATE ON SEBlock
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_StorageElement BEFORE UPDATE ON StorageElement
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_Block BEFORE UPDATE ON Block
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcDSStatus BEFORE UPDATE ON ProcDSStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_PrimaryDSType BEFORE UPDATE ON PrimaryDSType
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_QualityValues BEFORE UPDATE ON QualityValues
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_SubSystem BEFORE UPDATE ON SubSystem
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_RunLumiQuality BEFORE UPDATE ON RunLumiQuality
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();


CREATE TRIGGER UTR_RunLumiDQInt BEFORE UPDATE ON RunLumiDQInt
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();


CREATE TRIGGER UTR_QualityVersion BEFORE UPDATE ON QualityVersion
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_Branch BEFORE UPDATE ON Branch
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_BranchHash BEFORE UPDATE ON BranchHash
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_BranchHashMap BEFORE UPDATE ON BranchHashMap
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_FileProcQuality BEFORE UPDATE ON FileProcQuality
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_BlockParent BEFORE UPDATE ON BlockParent
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

CREATE TRIGGER UTR_ProcessStatus BEFORE UPDATE ON ProcessingStatus
FOR EACH ROW SET NEW.LastModificationDate = UNIX_TIMESTAMP();

-- ======================================================================
-- Initialize status tables There can be better ways to do it ( laters ) 
-- ======================================================================

INSERT INTO AnalysisDSStatus (Status, CreationDate) VALUES ('NEW', UNIX_TIMESTAMP());
INSERT INTO ProcDSStatus (Status, CreationDate) VALUES ('VALID', UNIX_TIMESTAMP()), ('INVALID', UNIX_TIMESTAMP()), ('PRODUCTION',
UNIX_TIMESTAMP()), ('DEPRECATED', UNIX_TIMESTAMP()), ('VALID-RO', UNIX_TIMESTAMP()), ('DELETED', UNIX_TIMESTAMP());
INSERT INTO FileStatus (Status, CreationDate) VALUES ('VALID', UNIX_TIMESTAMP()), ('INVALID', UNIX_TIMESTAMP()), ('MERGED', UNIX_TIMESTAMP()), ('IMPORTED', UNIX_TIMESTAMP()) , ('EXPORTED', UNIX_TIMESTAMP());
INSERT INTO FileValidStatus (Status, CreationDate) VALUES ('VALID', UNIX_TIMESTAMP()), ('INVALID', UNIX_TIMESTAMP());
INSERT INTO FileType(Type, CreationDate) VALUES ('EDM', UNIX_TIMESTAMP()) ;
INSERT INTO FileType(Type, CreationDate) VALUES ('STREAMER', UNIX_TIMESTAMP()) ;
INSERT INTO FileType(Type, CreationDate) VALUES ('PIXDMP', UNIX_TIMESTAMP()) ;
INSERT INTO FileType(Type, CreationDate) VALUES ('LUMI', UNIX_TIMESTAMP()) ;
INSERT INTO FileType(Type, CreationDate) VALUES ('LUMI-SA', UNIX_TIMESTAMP()) ;
INSERT INTO FileType(Type, CreationDate) VALUES ('LUMI-VDM', UNIX_TIMESTAMP()) ;
INSERT INTO AnalysisDSType(Type, CreationDate) VALUES ('TEST', UNIX_TIMESTAMP());
INSERT INTO PrimaryDSType  (Type, CreationDate) VALUES ('test', UNIX_TIMESTAMP()), ('data',  UNIX_TIMESTAMP()), ('raw', UNIX_TIMESTAMP()) , ('mc', UNIX_TIMESTAMP()), ('cosmic', UNIX_TIMESTAMP()), ('align', UNIX_TIMESTAMP()), ('calib', UNIX_TIMESTAMP());

INSERT INTO DataTier (Name, CreationDate) VALUES ('GEN', UNIX_TIMESTAMP()), ('SIM', UNIX_TIMESTAMP()), ('DIGI', UNIX_TIMESTAMP()), ('RECO', UNIX_TIMESTAMP()), ('ALCARECO', UNIX_TIMESTAMP()), ('USER', UNIX_TIMESTAMP()),  ('RAW', UNIX_TIMESTAMP()), ('AOD', UNIX_TIMESTAMP()), ('AODSIM', UNIX_TIMESTAMP()), ('HLTDEBUG', UNIX_TIMESTAMP()), ('GEN-SIM', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI', UNIX_TIMESTAMP()), ('GEN-SIM-RAW', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-RAW', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-HLTDEBUG', UNIX_TIMESTAMP()), ('GEN-SIM-RAW-HLTDEBUG', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-RAW-HLTDEBUG', UNIX_TIMESTAMP()), ('GEN-SIM-RECO', UNIX_TIMESTAMP()), ('GEN-SIM-RAW-RECO', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-RAW-RECO', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-HLTDEBUG-RECO', UNIX_TIMESTAMP()), ('GEN-SIM-RAW-HLTDEBUG-RECO', UNIX_TIMESTAMP()), ('FEVT', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-RAW-HLTDEBUG-RECO', UNIX_TIMESTAMP()), ('GEN-SIM-DIGI-RECO', UNIX_TIMESTAMP()), ('DIGI-RECO', UNIX_TIMESTAMP()), ('RAW-RECO', UNIX_TIMESTAMP()), ('FEVTDEBUGHLT', UNIX_TIMESTAMP());

INSERT INTO PhysicsGroup (PhysicsGroupName, CreationDate) VALUES ('Individual', UNIX_TIMESTAMP()), 
('Higgs', UNIX_TIMESTAMP()), 
('SUSYBSM', UNIX_TIMESTAMP()), 
('EWK', UNIX_TIMESTAMP()), 
('Top', UNIX_TIMESTAMP()), 
('QCD', UNIX_TIMESTAMP()), 
('Diffraction', UNIX_TIMESTAMP()), 
('OnSel', UNIX_TIMESTAMP()), 
('Bphys', UNIX_TIMESTAMP()), 
('Muons', UNIX_TIMESTAMP()), 
('Egamma', UNIX_TIMESTAMP()), 
('JetMet', UNIX_TIMESTAMP()), 
('PFlowTau', UNIX_TIMESTAMP()), 
('Btag', UNIX_TIMESTAMP()), 
('RelVal', UNIX_TIMESTAMP()), 
('Tracker', UNIX_TIMESTAMP()), 
('HeavyIon', UNIX_TIMESTAMP()), 
('PhysVal', UNIX_TIMESTAMP());

INSERT INTO QualityValues (Value, CreationDate) VALUES ("GOOD", UNIX_TIMESTAMP()),
                ("BAD", UNIX_TIMESTAMP()), ("UNKNOWN", UNIX_TIMESTAMP());

INSERT INTO ProcessingStatus(PROCESSINGSTATUS) values ('FAILED');
INSERT INTO ProcessingStatus(PROCESSINGSTATUS) values ('SUCCESS');

INSERT INTO SchemaVersion(SchemaVersion, InstanceName, InstanceType, CreationDate, DBS_RELEASE_VERSION) values
('DBS_1_1_6', 'LOCAL', 'MYSQL', UNIX_TIMESTAMP(), 'DBS_2_0_8');

commit;

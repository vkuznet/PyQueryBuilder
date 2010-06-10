drop table t2;
drop table t1;
create table t1 (t1key INTEGER PRIMARY KEY,data VARCHAR(30),num INTEGER,timeEnter DATE);
insert into t1 (t1key, data, num) values (1,'This is sample data',3);
insert into t1 (t1key, data, num) values (2,'More sample data',6);
insert into t1 (t1key, data, num) values (3,'And a little more',9);
create table t2 (t2key INTEGER PRIMARY KEY, t1key INTEGER, num INTEGER,timeEnter DATE,FOREIGN KEY (t1key) REFERENCES t1(t1key));

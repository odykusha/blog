drop table if exists notes;
create table notes (
 id integer primary key autoincrement,
 timestamp DATE DEFAULT (datetime('now','localtime')),
 text text not null,
 user_name text not null
);

drop table if exists users;
create table users (
 id integer primary key autoincrement,
 login text not null,
 password text not null,
 status integer DEFAULT 1
);
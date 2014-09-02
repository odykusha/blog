drop table if exists entries;
create table entries (
 id integer primary key autoincrement,
 timestamp DATE DEFAULT (datetime('now','localtime')),
 title text not null,
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
drop table if exists notes;
create table notes (
 id integer primary key autoincrement,
 timestamp DATE DEFAULT (datetime('now','localtime')),
 text text not null,
 user_id integer not null
);

drop table if exists users;
create table users (
 id integer primary key autoincrement,
 user_name text not null,
 password text not null,
 status integer DEFAULT 1
);

insert into users (id, user_name, password) values (0, 'admin', 'passwd')
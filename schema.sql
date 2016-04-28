drop table if exists notes;
create table notes (
 id integer primary key autoincrement,
 timestamp integer(4) not null default (strftime('%s','now')),
 text text not null,
 user_id integer not null,
 global_visible bool not null default 0
);

drop table if exists users;
create table users (
 id integer primary key autoincrement,
 user_name text not null,
 password text not null,
 status integer DEFAULT 1
);


drop table if exists users_new;
create table users_new (
 id integer primary key autoincrement,
 client_id integer not null,
 system text not null,
 user_name text not null,
 photo text not null,
 status integer DEFAULT 1,
 is_admin integer default 0
);

--insert into users (id, user_name, password) values (0, 'admin', 'passwd');
--insert into users (user_name, password) values ('oleg', 'qaz');

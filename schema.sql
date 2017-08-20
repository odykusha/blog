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
 client_id text not null,
 portal text not null,
 user_name text not null,
 photo text not null,
 status integer not null default 1,
 is_admin integer not null default 0
);

insert into users (id, client_id, portal, user_name, photo)
VALUES (0, 'null', 'null','Видаленні','http://new.vk.com/images/deactivated_50.png');


drop table if exists rand;
create table rand (
 id integer primary key autoincrement,
 first text,
 second text,
 other text
);

insert into rand (id, first, second, other)
values (0, 'first values', 'second values', 'other values');
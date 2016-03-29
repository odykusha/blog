# -*- coding: utf-8 -*-
# notes  --------------------------------------
get_all_notes = """
        select nt.id as id,
             nt.text as text,
        nt.timestamp as timestamp,
       usr.user_name as user_name
        from notes nt
        LEFT OUTER JOIN users usr ON nt.user_id = usr.id
        order by id desc
        """

get_user_notes = """
        select nt.id as id,
             nt.text as text,
        nt.timestamp as timestamp,
       usr.user_name as user_name
        from notes nt
        LEFT OUTER JOIN users usr ON nt.user_id = usr.id
        where usr.user_name = (?)
        order by id desc
        """

add_note = """
        insert into notes (text, user_id)
        values (?, ?)
        """

del_note = """
        delete from notes
        where id = (?)
        """

get_note_by_node_id = """
        select nt.id as id,
        nt.timestamp as timestamp,
             nt.text as text,
          nt.user_id as user_id,
       usr.user_name as user_name
        from notes nt
        LEFT OUTER JOIN users usr ON nt.user_id = usr.id
        where nt.id = (?)
        """

# users ---------------------------------------
get_all_users = """
        select id, user_name, password, status
        from users
        where id <> 0  --user_name: admin
        order by id desc
        """

get_user = """
        select id, user_name, password
        from users
        where user_name = (?)
        and password = (?)
        """

add_user = """
        insert into users (user_name, password)
        values (?, ?)
        """

del_user = """
        delete from users
        where id = (?)
        """

valid_user_name = """
        select user_name
        from users
        where user_name = (?)
        """
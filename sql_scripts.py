# -*- coding: utf-8 -*-
# notes  --------------------------------------
note_show = """
        select nt.id as id,
             nt.text as text,
        nt.timestamp as timestamp,
       usr.user_name as user_name
        from notes nt
        LEFT OUTER JOIN users usr ON nt.user_id = usr.id
        order by id desc
        """

note_add = """
        insert into notes (text, user_id)
        values (?, ?)
        """

note_del = """
        delete from notes
        where id = (?)
        """

get_note_by_node_id = """
        select id, timestamp, text, user_id
        from notes
        where id = (?)
        """

# users ---------------------------------------
users_show = """
        select id, user_name, password, status
        from users
        where id <> 0
        order by id desc
        """

users_get = """
        select id, user_name, password
        from users
        where user_name = (?)
        and password = (?)
        """

users_add = """
        insert into users (user_name, password)
        values (?, ?)
        """

users_valid = """
        select user_name
        from users
        where user_name = (?)
        """

users_del = """
        delete from users
        where id = (?)
        """
# -*- coding: utf-8 -*-
# notes  --------------------------------------
note_show = """
        select id, text, timestamp, user_name
        from notes
        order by id desc
        """

note_add = """
        insert into notes (text, user_name)
        values (?, ?)
        """

note_del = """
        delete from notes
        where id = (?)
        """

get_note_by_node_id = """
        select id, timestamp, text, user_name
        from notes
        where id = (?)
        """

# users ---------------------------------------
users_show = """
        select id, login, password, status
        from users
        order by id desc
        """

users_get = """
        select login, password
        from users
        where login = (?)
        and password = (?)
        """

users_add = """
        insert into users (login, password)
        values (?, ?)
        """

users_valid = """
        select login
        from users
        where login = (?)
        """

users_del = """
        delete from users
        where id = (?)
        """
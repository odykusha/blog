# -*- coding: utf-8 -*-
# entries --------------------------------------
entries_show = """
               select id, title, text, timestamp
               from entries
               order by id desc
               """

entries_add = """
              insert into entries (title, text)
              values (?, ?)
              """

entries_del = """
              delete from entries
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
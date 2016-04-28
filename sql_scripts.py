# -*- coding: utf-8 -*-
# notes  --------------------------------------
get_all_notes = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    usr.user_name as user_name,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users_new usr ON nt.user_id = usr.client_id
    where (nt.global_visible = 1 or usr.client_id = (?))
    order by id desc
    """

get_user_notes = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    usr.user_name as user_name,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users_new usr ON nt.user_id = usr.client_id
    where usr.user_name = (?)
    order by id desc
    """

get_notes_deleted_users = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    usr.user_name as user_name,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users_new usr ON nt.user_id = usr.client_id
    where usr.user_name is null
    order by id desc;
    """

add_note = """
    insert into notes (text, user_id, global_visible)
    values (?, ?, ?)
    """

change_note = """
    update notes
    set text = (?),
    global_visible = (?)
    where id = (?)
    """

get_note_by_node_id = """
    select nt.id as id,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    nt.text as text,
    nt.user_id as user_id,
    usr.user_name as user_name,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users_new usr ON nt.user_id = usr.client_id
    where nt.id = (?)
    """

del_note = """
    delete from notes
    where id = (?)
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

# users NEW!!! --------------------------------
update_insert_user = """
    INSERT OR REPLACE INTO users_new (id, client_id, portal, user_name, photo, status, is_admin)
    VALUES (  COALESCE((SELECT id FROM users_new WHERE client_id = (?)), null),
            (?), (?), (?), (?),
            COALESCE((SELECT status FROM users_new WHERE client_id = (?)), null),
            COALESCE((SELECT is_admin FROM users_new WHERE client_id = (?)), null)
            );
    """

get_user_head = """
    select status, is_admin
    from users_new
    where client_id = (?)
    """
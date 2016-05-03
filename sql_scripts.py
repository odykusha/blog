# -*- coding: utf-8 -*-
# notes  --------------------------------------
get_all_notes = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    usr.user_name as user_name,
    usr.id as user_id,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users usr ON nt.user_id = usr.id
    where (nt.global_visible = 1 or usr.id = (?))
    order by id desc
    """

get_user_notes = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    nt.user_id as user_id,
    usr.user_name as user_name,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users usr ON nt.user_id = usr.id
    where usr.id = (?)
    order by id desc
    """

get_notes_deleted_users = """
    select nt.id as id,
    nt.text as text,
    datetime(nt.timestamp, 'unixepoch', 'localtime') as timestamp,
    usr.user_name as user_name,
    usr.id as user_id,
    nt.global_visible as global_visible
    from notes nt
    LEFT OUTER JOIN users usr ON nt.user_id = usr.id
    where usr.id is null
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
    LEFT OUTER JOIN users usr ON nt.user_id = usr.id
    where nt.id = (?)
    """

del_note = """
    delete from notes
    where id = (?)
    """

# users ---------------------------------------
update_insert_user = """
    INSERT OR REPLACE INTO users (id, client_id, portal, user_name, photo, status, is_admin)
    VALUES (  COALESCE((SELECT id FROM users WHERE client_id = (?)), null),
            (?), (?), (?), (?),
            COALESCE((SELECT status FROM users WHERE client_id = (?)), null),
            COALESCE((SELECT is_admin FROM users WHERE client_id = (?)), null)
            );
    """

get_all_users = """
    select *
    from users
    order by id desc
    """

get_user = """
    select id, user_name, photo
    from users
    where id = (?)
    """

get_user_head = """
    select id, status, is_admin
    from users
    where client_id = (?)
    and portal = (?)
    """

del_user = """
    delete from users
    where id = (?)
    """
import functools
import sqlite3

from flask import session, redirect, url_for, render_template, request, jsonify, Blueprint

from view import app
from view.forms import BlogForm
from view.db_utils import get_db
from app_tools import note_filter, sql_scripts


view_notes = Blueprint('view_notes', __name__)
###############################################################################
# view
###############################################################################
# decorator logging
def logging(user_admin_session):
    """
    decorator for logging
    """
    def decor(func):
        @functools.wraps(func)
        def wrappers(*args, **kwargs):
            if not session.get(user_admin_session):
                return redirect(url_for('view_notes.login'))
            return func(*args, **kwargs)
        return wrappers
    return decor


@view_notes.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    session.pop('photo', None)
    return redirect(url_for('view_notes.show_notes'))


@view_notes.route('/', methods=['GET'])
@view_notes.route('/view/<int:note_id>', methods=["GET"])
@view_notes.route('/users/<int:user_id>', methods=['GET'])
def show_notes(user_id=None, note_id=None):
    PAGE = request.args.get('page', 0, type=int)
    form = BlogForm()
    db = get_db()

    if '?page=' in request.url:
        paginator = {'url_page': int(request.url.split('page=')[1]),
                     'url_user_id': user_id}
    else:
        paginator = {'url_page': 0,
                     'url_user_id': user_id}

    # записи видаленого користувача
    if user_id == 0:
        notes = db.execute(sql_scripts.get_notes_deleted_users,
                           [PAGE * app.config['MAX_NOTES_ON_PAGE'],
                            app.config['MAX_NOTES_ON_PAGE']]).fetchall()
        blog_form_visible = True
    # записи одного користувача
    elif user_id:
        notes = db.execute(sql_scripts.get_user_notes,
                           [user_id,
                            PAGE * app.config['MAX_NOTES_ON_PAGE'],
                            app.config['MAX_NOTES_ON_PAGE']]).fetchall()
        blog_form_visible = True
    # записи всіх користувачів
    else:
        notes = db.execute(sql_scripts.get_all_notes,
                           [session.get('user_id'),
                            PAGE * app.config['MAX_NOTES_ON_PAGE'],
                            app.config['MAX_NOTES_ON_PAGE']]).fetchall()
        blog_form_visible = False

    if note_id:
        notes = db.execute(sql_scripts.get_note_by_node_id, [note_id]).fetchall()
        try:
            if session.get('user_id') == notes[0]['user_id']:
                blog_form_visible = True
            else:
                blog_form_visible = False
        except:
            pass

    # user list
    cur = db.execute(sql_scripts.get_all_users)
    users = cur.fetchall()
    view_user = {}
    for i in users:
        if i['id'] == user_id:
            view_user['user_name'] = i['user_name']
            view_user['user_id']   = i['id']
            view_user['photo']     = i['photo']
    return render_template('show_notes.html',
                           blog_form_visible=blog_form_visible,
                           view_user=view_user,
                           notes=notes,
                           form=form,
                           users=users,
                           paginator=paginator)


@view_notes.route('/users/view/', methods=['GET'])
@logging('logged_admin')
def show_users():
    db = get_db()
    cur = db.execute(sql_scripts.get_all_users)
    users = cur.fetchall()
    return render_template('show_users.html', users=users)


# @app.route('/static/<filename>')
# # @cache.cached(timeout=5)
# def static_proxy(filename):
#     print("static: ", filename)
#     return app.send_static_file(filename)


###############################################################################
# AJAX function
###############################################################################
@view_notes.route('/ajax_create_note', methods=['POST'])
def ajax_create_note():
    note_text    = request.form['note_text']
    note_visible = request.form['note_visible']
    if note_visible == 'True':
        note_visible = True
    else:
        note_visible = False
    db = get_db()
    form = BlogForm()

    # перевірка на те, що користувач авторизувався
    if not session.get('logged_user'):
        return jsonify(status='ERR', message='спочатку необхідно авторизуватись')

    if form.submit() and len(note_text) > 0:
        db.execute(sql_scripts.add_note,
                   [note_filter.filter(note_text),
                    session.get('user_id'),
                    int(note_visible)])
        try:
            db.commit()
        except sqlite3.OperationalError:
            return jsonify(status='ERR', message='якесь гівно блочить базу')

        # дістаємо: note_id, user_name, timestamp
        cur = db.execute(sql_scripts.get_user_notes,
                         [session.get('user_id'),
                         0, 1])
        note = cur.fetchall()

        dict_for_html_gen = {'note_id'  : note[0]['id'],
                             'user_id'  : session.get('user_id'),
                             'user_name': session.get('user_name'),
                             'timestamp': note[0]['timestamp'],
                             'note_text': note_text,
                             'photo'    : session['photo']}
        return jsonify(status='OK', message='Додано запис, ІД:' + str(dict_for_html_gen['note_id']),
                       created_html_block = note_filter.generate_html_block_note(dict_for_html_gen))
    return jsonify(status='ERR', message='щось пішло не так')


@view_notes.route('/ajax_view_note', methods=['GET'])
def ajax_view_note():
    note_id = request.args.get('note_id', 0, type=int)

    db = get_db()
    cur = db.execute(sql_scripts.get_note_by_node_id, [note_id])
    note = cur.fetchall()
    # перевірка не дійсного запису
    if len(note) == 0:
        return jsonify(status='ERR', message='хуя тобі, вже нема такого запису')

    for nt in note:
        if nt['user_id'] == session.get('user_id') or session.get('logged_admin'):
            text = nt['text']
            visible = bool(nt['global_visible'])
            return jsonify(status='OK', note_text=text, visible_text=visible)
        else:
            return jsonify(status='ERR', message='чужі записи підглядати не добре')

    return jsonify(status='ERR', message='невідома помилка')


@view_notes.route('/ajax_change_note', methods=['POST'])
def ajax_change_note():
    note_id      = request.form['submit_id']
    note_text    = request.form['note_text']
    note_visible = request.form['note_visible']
    if note_visible == 'True':
        note_visible = True
    else:
        note_visible = False
    db = get_db()
    form = BlogForm()

    # змінювати запис може лише його автор
    cur = db.execute(sql_scripts.get_note_by_node_id, [note_id])
    note = cur.fetchall()
    for nt in note:
        if nt['user_id'] != session.get('user_id') and session.get('logged_admin') == None:
            return jsonify(status='ERR', message='От скотиняка нагла, не твій це запис')
    # збереження зміненого запису
    if form.submit_source() and len(note_text) > 0:
        db.execute(sql_scripts.change_note,
                   [note_text,
                    int(note_visible),
                    note_id])
        try:
            db.commit()
        except sqlite3.OperationalError:
            return jsonify(status='ERR', message='якесь гівно блочить базу')
        return jsonify(status='OK', message='Змінено запис, ІД:' + note_id)
    # по невідомим причинам
    return jsonify(status='ERR', message='я хз чому так вийшло')


@view_notes.route('/ajax_delete_note', methods=['DELETE'])
def ajax_delete_note():
    note_id = request.form['submit_id']
    db = get_db()

    # дістаємо логін користувача з ІД запису
    cur = db.execute(sql_scripts.get_note_by_node_id, [note_id])
    note = cur.fetchall()
    # перевірка видалення не дійсного запису
    if len(note) == 0:
        return jsonify(status='ERR', message='хуя тобі, вже нема такого запису')

    # видаляти може лише автор, або адмін
    elif note[0]['user_id'] == session.get('user_id') or session.get('logged_admin'):
        db.execute(sql_scripts.del_note, [note_id])
        try:
            db.commit()
        except sqlite3.OperationalError:
            return jsonify(status='ERR', message='якесь гівно блочить базу')
        return jsonify(status='OK', message='Видалено запис, ІД:' + note_id)

    # перевірка видалення чужого запису
    else:
        return jsonify(status='ERR', message='хитрожопий, ти не можеш видалити чужий запис')


@view_notes.route('/ajax_delete_user', methods=['DELETE'])
def ajax_delete_user():
    user_id = request.form['user_id']
    db = get_db()

    if session.get('logged_admin'):
        db.execute(sql_scripts.del_user, [user_id])
        try:
            db.commit()
        except sqlite3.OperationalError:
            return jsonify(status='ERR', message='якесь гівно блочить базу')
        return jsonify(status='OK', message='Видалено користувача, ІД:' + user_id)

    return jsonify(status='ERR', message='спочатку потрібно авторизуватись')
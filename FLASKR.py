# -*- coding: utf-8 -*-
import functools
import os
import sqlite3

from flask import Flask, session, g, redirect, url_for, render_template, request, jsonify
from flask.ext.wtf import Form
from wtforms import SubmitField, \
                    validators, TextAreaField, BooleanField

# from flask.ext.cache import Cache
# from flask_debugtoolbar import DebugToolbarExtension

from app_tools import tools, sql_scripts

###############################################################################
# Configuration
###############################################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')
DEBUG = True
SECRET_KEY = os.urandom(25)
CSRF_ENABLED = True
HOST = '0.0.0.0'
PORT = 8080

MAX_NOTES_ON_PAGE = 10

app = Flask(__name__)
app.config.from_object(__name__)
# cache = Cache(app,config={'CACHE_TYPE': 'simple'})
# tools = DebugToolbarExtension(app)


###############################################################################
# WTForm's
###############################################################################
class BlogForm(Form):
    blog_text = TextAreaField("text",
        [validators.Length(max=3, message='цей грьобаний текст ніколи не відобразиться')])
    visible_post = BooleanField("Видний усім")
    submit = SubmitField('Добавити')

    blog_text_source = TextAreaField("text")
    visible_post_source = BooleanField("Видний усім")
    submit_source = SubmitField('Змінити')


###############################################################################
# DB utils
###############################################################################
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """
    get DB session
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """
    close DB session
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    """
    create DB
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        #db.commit()


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
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrappers
    return decor


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    session.pop('photo', None)
    return redirect(url_for('show_notes'))


@app.route('/', methods=['GET'])
@app.route('/view/<int:note_id>', methods=["GET"])
@app.route('/users/<int:user_id>', methods=['GET'])
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
                           [PAGE * MAX_NOTES_ON_PAGE,
                            MAX_NOTES_ON_PAGE]).fetchall()
        blog_form_visible = True
    # записи одного користувача
    elif user_id:
        notes = db.execute(sql_scripts.get_user_notes,
                           [user_id,
                            PAGE * MAX_NOTES_ON_PAGE,
                            MAX_NOTES_ON_PAGE]).fetchall()
        blog_form_visible = True
    # записи всіх користувачів
    else:
        notes = db.execute(sql_scripts.get_all_notes,
                           [session.get('user_id'),
                            PAGE * MAX_NOTES_ON_PAGE,
                            MAX_NOTES_ON_PAGE]).fetchall()
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


@app.route('/users/view/', methods=['GET'])
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
# error
###############################################################################
@app.errorhandler(403)
def err403(error):
    message = "У вас немає прав для перегляду записів інших користувачів!<br> " + str(error)
    return render_template('error.html', error_message=message), 403


@app.errorhandler(404)
def err404(error):
    message = "Шукаєш те, чого немає!<br> " + str(error)
    return render_template('error.html', error_message=message), 404


@app.errorhandler(405)
def err405(error):
    message = "Такий метод не підтримується!<br> " + str(error)
    return render_template('error.html', error_message=message), 405


###############################################################################
# AJAX function
###############################################################################
@app.route('/ajax_create_note', methods=['POST'])
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
                   [tools.filter(note_text),
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

        user_id   = session.get('user_id')
        user_name = session.get('user_name')
        timestamp = note[0]['timestamp']
        note_id   = note[0]['id']

        return jsonify(status='OK', message='Додано запис, ІД:' + str(note_id),
            user_id=user_id,
            user_name=user_name,
            timestamp=timestamp,
            note_id=note_id)
    return jsonify(status='ERR', message='щось пішло не так')


@app.route('/ajax_view_note', methods=['GET'])
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


@app.route('/ajax_change_note', methods=['POST'])
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


@app.route('/ajax_delete_note', methods=['DELETE'])
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


@app.route('/ajax_delete_user', methods=['DELETE'])
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


###############################################################################
# auth API Vk
###############################################################################
import requests, json


CLIENT_ID = 5435272
CLIENT_SECRET = '5aYHQwz5S4BofTTA36g3'
# get uri link where running app
REDIRECT_URI = 'http://odykusha.pythonanywhere.com/get_access_token_vk'


@app.route('/auth_vk', methods=['GET'])
def auth_vk():
    if session.get('logged_user'):
        return redirect(url_for('show_notes'))
    # on local
    visual_res = {"access_token":"5ea99aae364db29f5610253844860575ab85cb447f4d931eb2c7013405b0c43ffc1b1f68208959d29e9ed","expires_in":86390,"user_id":137375300}
    return registration(visual_res)
    # on real
    get_user_code = requests.get(url='https://oauth.vk.com/authorize',
                                 params={'client_id': CLIENT_ID,
                                         'display':'page',
                                         'redirect_uri': REDIRECT_URI,
                                         'scope':'status',
                                         'response_type':'code',
                                         'v': '5.50'})
    request_status = get_user_code.status_code
    if request_status == 200:
        return redirect(get_user_code.url)
    else:
        return get_user_code.content, request_status


@app.route('/get_access_token_vk', methods=['GET'])
def get_access_token_vk():
    code = request.args.get('code')
    get_access_token = requests.get(url='https://oauth.vk.com/access_token',
                                    params={'client_id': CLIENT_ID,
                                            'client_secret': CLIENT_SECRET,
                                            'redirect_uri': REDIRECT_URI,
                                            'code': code})
    request_status = get_access_token.status_code
    if request_status != 200:
        return get_access_token.content, request_status

    access_dict = json.loads(get_access_token.text)
    print("|| access_dict ||", access_dict)
    registration(access_dict)



def registration(access_dict):
    get_client_info = requests.get(url='https://api.vk.com/method/users.get',
                                   params={'user_id': access_dict['user_id'],
                                           'v': '5.50',
                                           'fields': 'first_name,last_name,photo',
                                           'access_token': access_dict['access_token']})
    request_status = get_client_info.status_code
    if request_status != 200:
        return get_client_info.content, request_status

    client_dict = json.loads(get_client_info.text)

    if 'error' in client_dict:
        return client_dict, 401



    client_dict = client_dict.get('response')[0]
    session['logged_user'] = True
    session['user_name'] = client_dict.get('first_name') + ' ' + \
                           client_dict.get('last_name')
    session['photo'] = client_dict.get('photo')
    auth_user_id = client_dict.get('id')
    client_portal = 'vk.com'

    db = get_db()
    db.execute(sql_scripts.update_insert_user,
                    [auth_user_id,
                     auth_user_id,
                     client_portal,
                     session.get('user_name'),
                     session.get('photo'),
                     auth_user_id,
                     auth_user_id])
    db.commit()


    # add admin role
    cur = db.execute(sql_scripts.get_user_head,
                     [auth_user_id,
                      client_portal]).fetchall()
    for cr in cur:
        session['user_id'] = cr['id']
        if cr['is_admin']:
            session['logged_admin'] = True
        user_status = cr['status']

    return redirect(url_for('show_notes', user_id=session.get('user_id')))


###############################################################################
if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
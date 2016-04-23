# -*- coding: utf-8 -*-
import os
import functools
import sqlite3

from flask import Flask, session, g, redirect, url_for, render_template, flash, \
                  request, abort, jsonify
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, \
                    validators, TextAreaField, BooleanField
# from flask.ext.cache import Cache
# from flask_debugtoolbar import DebugToolbarExtension

import sql_scripts
import tools


###############################################################################
# Configuration
###############################################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')
DEBUG = True
SECRET_KEY = os.urandom(25)
CSRF_ENABLED = True
HOST = '0.0.0.0'
PORT = 80

app = Flask(__name__)
app.config.from_object(__name__)
# cache = Cache(app,config={'CACHE_TYPE': 'simple'})
# tools = DebugToolbarExtension(app)


###############################################################################
# WTForm's
###############################################################################
class LoginForm(Form):
    psw_min = 3
    psw_max = 15
    auth_login = StringField('Логін',
        [validators.DataRequired(message='логін не може бути пустим')])

    auth_password = PasswordField('Пароль',
        [validators.Length(min=psw_min, max=psw_max,
        message='пароль має бути від %s до %s символів' % (psw_min, psw_max))])

    submit = SubmitField('Зайти')


class UserForm(Form):
    len_min = 3
    len_max = 15
    user_login = StringField('Логін користувача',
        [validators.DataRequired(message='логін не може бути пустим'),
         validators.Length(min=len_min, max=len_max,
         message='логін має бути від %s до %s символів' % (len_min, len_max))])

    user_password = StringField('Пароль користувача',
        [validators.Length(min=len_min, max=len_max,
        message='пароль має бути від %s до %s символів' % (len_min, len_max))])

    submit = SubmitField('Добавити')


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


def login_in_db(login):
    db = get_db()
    cur = db.execute(sql_scripts.valid_user_name, [login]).fetchall()
    for i in cur:
        if i['user_name'] == login:
            return True
    return False


def init_db():
    """
    create DB
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        #db.commit()


def show_db(db_name):
    """
    show DB content
    """
    with app.app_context():
        db = get_db()
        if db_name == 'notes':
            cur_nt = db.execute("""
                         select *
                         from notes
                         """)
            rows = cur_nt.fetchall()
            print(('ID', 'timestamp', 'Text', 'User_id', 'global_visible'))
            for row in rows:
                print((row['id'],
                      row['timestamp'],
                      row['text'],
                      row['user_id'],
                      row['global_visible']))

        elif db_name == 'users':
            cur_us = db.execute("""
                         select *
                         from users
                         """)
            rows = cur_us.fetchall()
            print(('ID', 'User_name', 'Password', 'Status'))
            for row in rows:
                print((row['id'],
                      row['user_name'],
                      row['password'],
                      row['status']))


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


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if session.get('logged_user'):
        return redirect(url_for('show_notes'))

    error = None
    db_login = None
    db_pass = None
    form = LoginForm()

    if form.validate_on_submit():
        # перевірить наявність в базі
        db = get_db()
        cur = db.execute(sql_scripts.get_user,
                [form.auth_login.data, form.auth_password.data]).fetchall()
        for c in cur:
            db_id    = c['id']
            db_login = c['user_name']
            db_pass  = c['password']

        if not login_in_db(form.auth_login.data):
            error = 'Логін не знайдено'
        elif form.auth_password.data != db_pass:
            error = 'Невірний пароль'
        else:
            session['logged_user'] = True
            session['user_name']   = form.auth_login.data
            session['user_id']     = db_id
            if db_login == 'admin':
                session['logged_admin'] = True
            flash('Ви успішно авторизуватись, привіт %s' % form.auth_login.data)
            return redirect(url_for('show_notes', user_name=session.get('user_name')))
    return render_template('login.html', error=error, form=form)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect(url_for('show_notes'))


@app.route('/', methods=['GET'])
@app.route('/users/<user_name>', methods=['GET'])
def show_notes(user_name=None):
    db = get_db()
    form = BlogForm()
    if user_name:
        cur = db.execute(sql_scripts.get_user_notes, [user_name])
        blog_form_visible = True
    else:
        cur = db.execute(sql_scripts.get_all_notes, [session.get('user_id')])
        blog_form_visible = False
    # note list
    notes = cur.fetchall()
    # user list
    cur = db.execute(sql_scripts.get_all_users)
    users = cur.fetchall()
    return render_template('show_notes.html',
                           blog_form_visible=blog_form_visible,
                           view_user=user_name,
                           notes=notes,
                           form=form,
                           users=users)


@app.route('/users/view/', methods=['GET'])
@logging('logged_admin')
def show_users(form=None):
    db = get_db()
    if not form:
        form = UserForm()
    cur = db.execute(sql_scripts.get_all_users)
    users = cur.fetchall()
    return render_template('show_users.html', users=users, form=form)


@app.route('/users/add/', methods=['POST'])
@logging('logged_admin')
def add_users():
    db = get_db()
    form = UserForm()
    if form.validate_on_submit():
        if login_in_db(form.user_login.data):
            flash('Такий логін вже є')
        else:
            db.execute(sql_scripts.add_user,
                      [form.user_login.data, form.user_password.data])
            flash('Юзер успішно добавлений')
            db.commit()
            form.user_login.data = ''
            form.user_password.data = ''
    return show_users(form)


@app.route('/users/del/<us_id>', methods=['POST'])
@logging('logged_admin')
def del_users(us_id):
    db = get_db()
    db.execute(sql_scripts.del_user, [us_id])
    db.commit()
    flash('Користувач видалений')
    return redirect(url_for('show_users'))


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
    return "У вас немає прав для перегляду записів інших користувачів!<br> %s" % error, 403


@app.errorhandler(404)
def err404(error):
    return "Шукаєш те, чого немає!<br> %s" % error, 404


@app.errorhandler(405)
def err405(error):
    return "Такий метод не підтримується!<br> %s" % error, 405


###############################################################################
# AJAX function
###############################################################################
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
            return jsonify(status='ERR', message='От скотиняка нагла')
    # збереження зміненого запису
    if form.submit_source() and len(note_text) > 0:
        db.execute(sql_scripts.change_note,
                   [note_text,
                    int(note_visible),
                    note_id])
        db.commit()
        return jsonify(status='OK', message='запис ID:' + note_id + ', успішно змінено')
    # по невідомим причинам
    return jsonify(status='ERR', message='я хз чому так вийшло')


@app.route('/ajax_delete_note', methods=['POST'])
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
        db.commit()
        return jsonify(status='OK', message='запис ID:' + note_id + ', успішно видалений')

    # перевірка видалення чужого запису
    else:
        return jsonify(status='ERR', message='хитрожопий, ти не можеш видалити чужий запис')


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
        db.commit()
        # take: note_id, user_name, timestamp
        cur = db.execute(sql_scripts.get_user_notes,
                        [session.get('user_name')])
        note = cur.fetchall()

        user_name = session.get('user_name')
        timestamp = note[0]['timestamp']
        note_id   = note[0]['id']

        return jsonify(status='OK', message='запис успішно додано',
            user_name=user_name,
            timestamp=timestamp,
            note_id=note_id)
    return jsonify(status='ERR', message='щось пішло не так')



#  sqlite3.OperationalError: database is locked


###############################################################################
if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
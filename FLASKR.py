# -*- coding: utf-8 -*-
import os
import functools
import sqlite3

from flask import Flask, session, g, redirect, url_for, render_template, flash, \
                  request, abort
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, \
                    validators, TextAreaField
# from flask.ext.cache import Cache
#from flask_debugtoolbar import DebugToolbarExtension

import sql_scripts

###############################################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')
DEBUG = True
SECRET_KEY = os.urandom(25)
CSRF_ENABLED = True
HOST = '127.0.0.1'
PORT = 8080

app = Flask(__name__)
app.config.from_object(__name__)
# cache = Cache(app,config={'CACHE_TYPE': 'simple'})
#tools = DebugToolbarExtension(app)

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
        [validators.Length(max=3, message='чому ти сука не працюєш')])

    submit = SubmitField('Добавити')


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
            print(('ID', 'timestamp', 'Text', 'User_id'))
            for row in rows:
                print((row['id'],
                      row['timestamp'],
                      row['text'],
                      row['user_id']))

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
            return redirect(url_for('show_notes'))
    return render_template('login.html', error=error, form=form)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET'])
#@logging('logged_user')
def show_notes():
    db = get_db()
    form = BlogForm()
    cur = db.execute(sql_scripts.get_all_notes)
    notes = cur.fetchall()
    return render_template('show_notes.html', notes=notes, form=form)


@app.route('/users/<user_name>', methods=['GET'])
@logging('logged_user')
def user_notes(user_name):
    if session.get('user_name') == user_name or session.get('logged_admin'):
        db = get_db()
        form = BlogForm()
        cur = db.execute(sql_scripts.get_user_notes, [user_name])
        notes = cur.fetchall()
        return render_template('show_notes.html', notes=notes, form=form)
    else:
        abort(403)


@app.route('/notes_source/<note_id>', methods=['GET'])
@logging('logged_admin')
def show_note_source(note_id):
    db = get_db()
    cur = db.execute(sql_scripts.get_note_by_node_id, [note_id])
    note = cur.fetchall()
    return render_template('show_note_source.html', note=note)


@app.route('/add/', methods=['POST'])
@logging('logged_user')
def add_note():
    db = get_db()
    form = BlogForm()
    if form.submit() and len(form.blog_text.data) > 0:
        db.execute(sql_scripts.add_note,
                   [form.blog_text.data,
                    session.get('user_id')])
        db.commit()
        flash('пост додано')
    return redirect(url_for('show_notes'))


@app.route('/del/<int:note_id>', methods=['POST'])
@logging('logged_user')
def del_note(note_id):
    db = get_db()
    # дістаємо логін користувача з ІД посту
    cur = db.execute(sql_scripts.get_note_by_node_id, [note_id])
    note = cur.fetchall()
    # перевірка видалення не дійсного посту
    if len(note) == 0:
        flash('хуя тобі, вже нема такого поста')
    # видаляти може лише автор, або адмін
    elif note[0]['user_id'] == session.get('user_id') or session.get('logged_admin'):
        db.execute(sql_scripts.del_note, [note_id])
        db.commit()
        flash('пост видалено')
    # перевірка видалення чужого поста
    else:
        flash('хитрожопий, ти не можеш видалити чужий пост')
    return redirect(url_for('show_notes'))


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
    return "У вас немає прав для перегляду постів інших користувачів!<br> %s" % error, 403


@app.errorhandler(404)
def err404(error):
    return "Шукаєш те, чого немає!<br> %s" % error, 404


@app.errorhandler(405)
def err405(error):
    return "Такий метод не підтримується!<br> %s" % error, 405


###############################################################################
if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
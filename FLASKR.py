# -*- coding: utf-8 -*-
import os
import functools
import sqlite3

from flask import Flask, session, g, redirect, \
                  url_for, render_template, flash
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, \
                    validators, TextAreaField

import sql_scripts

###############################################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')
DEBUG = True
SECRET_KEY = os.urandom(25)
USERNAME = 'admin'
PASSWORD = 'passwd'
CSRF_ENABLED = True

app = Flask(__name__)
app.config.from_object(__name__)


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


def init_db():
    """
    create DB
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        #db.commit()


def valid_login(login):
    if login == app.config['USERNAME']:
        return False
    db = get_db()
    cur = db.execute(sql_scripts.users_valid, [login]).fetchall()
    for i in cur:
        if i['login'] == login:
            return False
    #else
    return True


def show_db(db_name):
    """
    show DB content
    """
    with app.app_context():
        db = get_db()
        cur_en = db.execute("""
                         select *
                         from notes
                         """)
        cur_us = db.execute("""
                         select *
                         from users
                         """)

        if db_name == 'notes':
            rows = cur_en.fetchall()
            print(('ID', 'timestamp', 'Text', 'User_name'))
            for row in rows:
                print((row['id'],
                      row['timestamp'],
                      row['text'],
                      row['user_name']))
        elif db_name == 'users':
            rows = cur_us.fetchall()
            print(('ID', 'Login', 'Password', 'Status'))
            for row in rows:
                print((row['id'],
                      row['login'],
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
    error = None
    db_login = None
    db_pass = None
    form = LoginForm()

    if form.validate_on_submit():
        # перевірити з локальних налаштувань
        if form.auth_login.data != app.config['USERNAME']:
            error = 'Логін не знайдено'
        elif form.auth_password.data != app.config['PASSWORD']:
            error = 'Пароль невірний'
        else:
            session['logged_user'] = True
            session['logged_admin'] = True
            session['user_name'] = form.auth_login.data
            flash('Ви успішно авторизуватись, як адмін')
            return redirect(url_for('show_notes'))
        # перевірить наявність в базі
        db = get_db()
        cur = db.execute(sql_scripts.users_get,
                [form.auth_login.data, form.auth_password.data]).fetchall()
        for i in cur:
            db_login = i['login']
            db_pass = i['password']
        if form.auth_login.data != db_login and form.auth_login.data != app.config['USERNAME']:
            error = 'Логін не знайдено'
        elif form.auth_password.data != db_pass:
            error = 'Пароль невірний'
        else:
            session['logged_user'] = True
            session['user_name'] = form.auth_login.data
            flash('Ви успішно авторизуватись, привіт %s' % form.auth_login.data)
            return redirect(url_for('show_notes'))
    return render_template('login.html', error=error, form=form)


@app.route('/logout')
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    return redirect(url_for('login'))


@app.route('/')
@logging('logged_user')
def show_notes():
    db = get_db()
    form = BlogForm()
    cur = db.execute(sql_scripts.note_show)
    notes = cur.fetchall()
    return render_template('show_notes.html', notes=notes, form=form)


@app.route('/add/', methods=['POST'])
@logging('logged_user')
def add_note():
    db = get_db()
    form = BlogForm()
    if form.submit() and len(form.blog_text.data) > 0:
        db.execute(sql_scripts.note_add,
                   [form.blog_text.data,
                    session.get('user_name')])
        db.commit()
        flash('пост додано')
    return redirect(url_for('show_notes'))


@app.route('/del/<nt_id>', methods=['POST', 'GET'])
@logging('logged_user')
def del_note(nt_id):
    db = get_db()
    # дістаємо логін користувача з ІД посту
    cur = db.execute(sql_scripts.get_user_by_note_id, [nt_id])
    delete_from_user = cur.fetchall()
    # перевірка видалення не дійсного посту
    if len(delete_from_user) == 0:
        return redirect(url_for('show_notes'))
    # видаляти може лише автор, або адмін
    if delete_from_user[0]['user_name'] == session['user_name'] or session.get('logged_admin'):
        db.execute(sql_scripts.note_del, [nt_id])
        db.commit()
        flash('пост видалено')
    return redirect(url_for('show_notes'))


@app.route('/users/', methods=['GET'])
@logging('logged_admin')
def show_users(form=None):
    db = get_db()
    if not form:
        form = UserForm()
    cur = db.execute(sql_scripts.users_show)
    users = cur.fetchall()
    return render_template('show_users.html', users=users, form=form)


@app.route('/users/add/', methods=['POST'])
@logging('logged_admin')
def add_users():
    db = get_db()
    form = UserForm()
    if form.validate_on_submit():
        if not valid_login(form.user_login.data):
            flash('Такий логін вже є')
        else:
            db.execute(sql_scripts.users_add,
                      [form.user_login.data, form.user_password.data])
            flash('Юзер успішно добавлений')
            db.commit()
            form.user_login.data = ''
            form.user_password.data = ''
    #return redirect(url_for('show_users', form=form))
    return show_users(form)


@app.route('/users/del/<us_id>', methods=['POST', 'GET'])
@logging('logged_admin')
def del_users(us_id):
    db = get_db()
    db.execute(sql_scripts.users_del, [us_id])
    db.commit()
    flash('Користувач видалений')
    return redirect(url_for('show_users'))


###############################################################################
# error
###############################################################################
#@app.errorhandler(401)
#def err401(error):
    #flash("Ви не авторизувались! %s" % error)
    #return redirect(url_for('show_entries'))


###############################################################################
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
from flask import Flask, request, session, g, redirect, \
                  url_for, abort, render_template, flash
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, validators, TextAreaField
import sqlite3
import os
import functools
import sql_scripts

# ---------------------------------------------
# config
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = os.urandom(25)
USERNAME = 'admin'
PASSWORD = 'passwd'
CSRF_ENABLED = True

app = Flask(__name__)
app.config.from_object(__name__)

# app.config.update(dict(
#     DATABASE=os.path.join(app.root_path, 'flaskr.db'),
#     DEBUG=True,
#     SECRET_KEY='some secret key',
#     USERNAME='admin',
#     PASSWORD='passwd'
# ))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# ---------------------------------------------
# class WTForm's
class LoginForm(Form):
    psw_min = 3
    psw_max = 15
    auth_login = StringField('Логін',  [validators.DataRequired(message='логін не може бути пустим')])
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
    blog_title = StringField('Заголовок')
    blog_text = TextAreaField('Текст')
    submit = SubmitField('Добавити')


# ---------------------------------------------
# DB utils
def connect_db():
    """
    connect to DB
    """
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


@app.before_first_request
def first_visit():
    return redirect(url_for('login'))


def init_db():
    """
    create DB
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            #db.executescript(f.read())
        db.commit()


def show_db(db_name):
    """
    show DB content
    """
    with app.app_context():
        db = get_db()
        cur_en = db.execute("""
                         select *
                         from entries
                         """)
        cur_us = db.execute("""
                         select *
                         from users
                         """)
        if db_name == 'entries':
            en = cur_en.fetchall()
        elif db_name == 'users':
            en = cur_us.fetchall()
    for i in en:
        print('ID:', i[0])
        print('TITLE:', i[1])
        print('TEXT:', i[2])
        print('DATE:', i[3], end='\n\n')  # lint:ok


def valid_login(login):
    if login == app.config['USERNAME']:
        return False
    db = get_db()
    cur = db.execute(sql_scripts.users_valid, [login]).fetchall()
    for i in cur:
        if i[0] == login:
            return False
    #else
    return True
# ---------------------------------------------
# view


class Logging(object):
    def __init__(self, wrapper):
        self.wrapper = wrapper
        functools.update_wrapper(self, wrapper)
    def __call__(self, *args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
       # elif session.get('logged_in') and not session.get('admin'):
       #     abort(401)
        return self.wrapper(*args, **kwargs)



@app.route('/')
@Logging
def show_entries():
    #if not session.get('logged_in'):
    #    return redirect(url_for('login'))
    db = get_db()
    form = BlogForm()
    cur = db.execute(sql_scripts.entries_show)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, form=form)


@app.route('/add/', methods=['POST'])
@Logging
def add_entry():
#    if not session.get('logged_in'):
#        abort(401)
    db = get_db()
    form = BlogForm()
    if form.submit():
        if form.blog_title.data == '' or form.blog_text.data == '':
            flash('"Заголовок" або "Текст" має бути не пустим!')
            return redirect(url_for('show_entries'))
        db.execute(sql_scripts.entries_add,
                   [form.blog_title.data, form.blog_text.data, session.get('user_name')])
        db.commit()
        flash('пост додано')
    return redirect(url_for('show_entries'))


@app.route('/del/<en_id>', methods=['POST', 'GET'])
@Logging
def del_entry(en_id):
#    if not session.get('logged_in'):
#        abort(401)
    db = get_db()
    db.execute(sql_scripts.entries_del, [en_id])
    db.commit()
    flash('пост видалено')
    return redirect(url_for('show_entries'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    db_login = None
    db_pass = None
    form = LoginForm()

    if form.validate_on_submit():

        db = get_db()
        cur = db.execute(sql_scripts.users_get,
                [form.auth_login.data, form.auth_password.data]).fetchall()
        for i in cur:
            db_login = i[0]
            db_pass = i[1]

        if form.auth_login.data != app.config['USERNAME']:
            error = 'Логін не знайдено'
        elif form.auth_password.data != app.config['PASSWORD']:
            error = 'Пароль невірний'
        else:
            session['logged_in'] = True
            session['admin'] = True
            session['user_name'] = form.auth_login.data
            flash('Ви успішно авторизуватись')
            return redirect(url_for('show_entries'))

        if form.auth_login.data != db_login and form.auth_login.data != app.config['USERNAME']:
            error = 'Логін не знайдено'
        elif form.auth_password.data != db_pass:
            error = 'Пароль невірний'
        else:
            session['logged_in'] = True
            session['user_name'] = form.auth_login.data
            flash('Ви успішно авторизуватись')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error=error, form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('admin', None)
    flash('Ви вийшли')
    return redirect(url_for('login'))


@app.route('/users/', methods=['GET'])
def show_users(form=None):
    if not session.get('admin'):
        abort(401)
    db = get_db()
    if not form:
        form = UserForm()
    cur = db.execute(sql_scripts.users_show)
    users = cur.fetchall()
    return render_template('show_users.html', users=users, form=form)


@app.route('/users/add/', methods=['POST'])
def add_users():
    if not session.get('admin'):
        abort(401)

    db = get_db()
    form = UserForm()
    if form.validate_on_submit():
        if not valid_login(form.user_login.data):
            flash('Логін вже є')
        else:
            db.execute(sql_scripts.users_add,
                      [form.user_login.data, form.user_password.data])
            flash('юзер успішно добавлений')
            db.commit()
            form.user_login.data=''
            form.user_password.data=''
    #return redirect(url_for('show_users', form=form))
    return show_users(form)


@app.route('/users/del/<us_id>', methods=['POST', 'GET'])
def del_users(us_id):
    if not session.get('admin'):
        abort(401)
    db = get_db()
    db.execute(sql_scripts.users_del, [us_id])
    db.commit()
    flash('Користувач видалений')
    return redirect(url_for('show_users'))


# ---------------------------------------------
# error


@app.errorhandler(401)
def err401(error):
    flash("Ви не авторизувались! %s" % error)
    return redirect(url_for('show_entries'))
# ---------------------------------------------
# start
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

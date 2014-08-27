from flask import Flask, request, session, g, redirect, \
                  url_for, abort, render_template, flash
import sqlite3
import os
import sql_scripts
# ---------------------------------------------
# config
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'some key'
USERNAME = 'admin'
PASSWORD = 'passwd'


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='some secret key',
    USERNAME='admin',
    PASSWORD='passwd'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


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


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute(sql_scripts.entries_show)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add/', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.form['title'] == '' or request.form['text'] == '':
        flash('"Заголовок" або "Текст" має бути не пустим!')
        return redirect(url_for('show_entries'))
    db.execute(sql_scripts.entries_add,
               [request.form['title'], request.form['text']])
    db.commit()
    flash('пост додано')
    return redirect(url_for('show_entries'))


@app.route('/del/<en_id>', methods=['POST', 'GET'])
def del_entry(en_id):
    if not session.get('logged_in'):
        abort(401)
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
    if request.method == 'POST':
        db = get_db()
        cur = db.execute(sql_scripts.users_get,
                [request.form['username'], request.form['password']]).fetchall()
        for i in cur:
            db_login = i[0]
            db_pass = i[1]


        if request.form['username'] != app.config['USERNAME']:
            error = 'Логін не знайдено'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Пароль невірний'
        else:
            session['logged_in'] = True
            session['admin'] = True
            flash('Ви успішно авторизуватись')
            return redirect(url_for('show_entries'))


        if request.form['username'] != db_login:
            error = 'Логін не знайдено'
        elif request.form['password'] != db_pass:
            error = 'Пароль невірний'
        else:
            session['logged_in'] = True
            flash('Ви успішно авторизуватись')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error=error)


@app.route('/users/', methods=['GET'])
def show_users():
    db = get_db()
    cur = db.execute(sql_scripts.users_show)
    users = cur.fetchall()
    return render_template('show_users.html', users=users)


@app.route('/users/add/', methods=['POST'])
def add_users():
    if not session['admin']:
        abort(401)

    db = get_db()
    if not valid_login(request.form['username']):
        flash('Логін вже є')
    elif len(request.form['password']) < 3:
        flash('Пароль закороткий')
    else:
        db.execute(sql_scripts.users_add,
                   [request.form['username'], request.form['password']])
        flash('успішно добавлений юзер')
        db.commit()
    return redirect(url_for('show_users'))


@app.route('/users/del/<us_id>', methods=['POST', 'GET'])
def del_users(us_id):
    if not session['admin']:
        abort(401)
    db = get_db()
    db.execute(sql_scripts.users_del, [us_id])
    db.commit()
    flash('Користувач видалений')
    return redirect(url_for('show_users'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('admin', None)
    flash('Ви вийшли')
    return redirect(url_for('show_entries'))
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

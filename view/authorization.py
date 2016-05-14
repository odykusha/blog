import requests, json, jwt

from flask import Blueprint
view_auth = Blueprint('view_auth', __name__)



from view import app
from app_tools import note_filter, sql_scripts

import functools
import sqlite3

from flask import Flask, session, g, redirect, url_for, render_template, request, jsonify
from flask.ext.wtf import Form
from wtforms import SubmitField, \
                    validators, TextAreaField, BooleanField

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
                return redirect(url_for('view_auth.login'))
            return func(*args, **kwargs)
        return wrappers
    return decor


@view_auth.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    session.pop('photo', None)
    return redirect(url_for('view_auth.show_notes'))


@view_auth.route('/', methods=['GET'])
@view_auth.route('/view/<int:note_id>', methods=["GET"])
@view_auth.route('/users/<int:user_id>', methods=['GET'])
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


@view_auth.route('/users/view/', methods=['GET'])
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
@view_auth.errorhandler(403)
def err403(error):
    message = "У вас немає прав для перегляду записів інших користувачів!<br> " + str(error)
    return render_template('error.html', error_message=message), 403


@view_auth.errorhandler(404)
def err404(error):
    message = "Шукаєш те, чого немає!<br> " + str(error)
    return render_template('error.html', error_message=message), 404


@view_auth.errorhandler(405)
def err405(error):
    message = "Такий метод не підтримується!<br> " + str(error)
    return render_template('error.html', error_message=message), 405


###############################################################################
# AJAX function
###############################################################################
@view_auth.route('/ajax_create_note', methods=['POST'])
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


@view_auth.route('/ajax_view_note', methods=['GET'])
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


@view_auth.route('/ajax_change_note', methods=['POST'])
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


@view_auth.route('/ajax_delete_note', methods=['DELETE'])
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


@view_auth.route('/ajax_delete_user', methods=['DELETE'])
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
# auth API VK.com
###############################################################################
# for VK
# http://new.vk.com/editapp?id=5435272&section=options
CLIENT_ID_for_vk = 5435272
CLIENT_SECRET_for_vk = '5aYHQwz5S4BofTTA36g3'
REDIRECT_URI_for_vk = 'http://odykusha.pythonanywhere.com/get_access_token_vk'
# for google+
# https://console.developers.google.com/apis/credentials/oauthclient/678971134005-p04u8p3iq8tt6th81n9i5bq15i7ma851.apps.googleusercontent.com?project=blog-on-flask
CLIENT_ID_for_gplus = '678971134005-p04u8p3iq8tt6th81n9i5bq15i7ma851.apps.googleusercontent.com'
CLIENT_SECRET_for_gplus = 'cVOM2T1TrnXgK3jkkVv_jOl7'
REDIRECT_URI_for_gplus = 'https://odykusha.pythonanywhere.com/get_access_token_gplus'


# VK
@view_auth.route('/auth_vk', methods=['GET'])
def auth_vk():
    if session.get('logged_user'):
        return redirect(url_for('view_auth.show_notes'))
    # on local
    visual_res = {"access_token":"948db4ec1c612fcd39819d24a2a9ba26bb22cb92edc46f1d74b2781db10cde8696630ecb75ce8b22ee35c","expires_in":86380,"user_id":137375300}
    return registration_vk(visual_res)
    # on real
    get_user_code = requests.get(url='https://oauth.vk.com/authorize',
                                 params={'client_id': CLIENT_ID_for_vk,
                                         'display':'page',
                                         'redirect_uri': REDIRECT_URI_for_vk,
                                         'scope':'status',
                                         'response_type':'code',
                                         'v': '5.50'})
    request_status = get_user_code.status_code
    if request_status == 200:
        return redirect(get_user_code.url)
    else:
        return get_user_code.content, request_status


@view_auth.route('/get_access_token_vk', methods=['GET'])
def get_access_token_vk():
    code = request.args.get('code')
    get_access_token = requests.get(url='https://oauth.vk.com/access_token',
                                    params={'client_id': CLIENT_ID_for_vk,
                                            'client_secret': CLIENT_SECRET_for_vk,
                                            'redirect_uri': REDIRECT_URI_for_vk,
                                            'code': code})
    request_status = get_access_token.status_code
    if request_status != 200:
        return get_access_token.content, request_status

    access_dict = json.loads(get_access_token.text)
    registration_vk(access_dict)


def registration_vk(access_dict):
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

    return redirect(url_for('view_auth.show_notes', user_id=session.get('user_id')))


###############################################################################
# auth API Google+
###############################################################################
# Google+
@view_auth.route('/auth_gplus', methods=['GET'])
def auth_gplus():
    if session.get('logged_user'):
        return redirect(url_for('view_auth.show_notes'))
    # on local
    visual_res = {'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImU3ZGJmNTI2ZjYzOWMyMTRjZDc3YjM5NmVjYjlkN2Y4MWQ0N2IzODIifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdF9oYXNoIjoiODJMejZvWnY1MEtaWVBONElMMDJKZyIsImF1ZCI6IjY3ODk3MTEzNDAwNS1wMDR1OHAzaXE4dHQ2dGg4MW45aTVicTE1aTdtYTg1MS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwNDMwMjI3MDk3MDYwMjI3OTc2NSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhenAiOiI2Nzg5NzExMzQwMDUtcDA0dThwM2lxOHR0NnRoODFuOWk1YnExNWk3bWE4NTEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJoZCI6InNtYXJ0d2ViLmNvbS51YSIsImVtYWlsIjoiby5kaWt1c2hhQHNtYXJ0d2ViLmNvbS51YSIsImlhdCI6MTQ2MzE1MTAyMywiZXhwIjoxNDYzMTU0NjIzLCJuYW1lIjoi0J7Qu9C10LMg0JTQuNC60YPRiNCwIiwicGljdHVyZSI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tTHhmUVNjTkx5MDgvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQk0vbmhEaEVtYVY5encvczk2LWMvcGhvdG8uanBnIiwiZ2l2ZW5fbmFtZSI6ItCe0LvQtdCzIiwiZmFtaWx5X25hbWUiOiLQlNC40LrRg9GI0LAiLCJsb2NhbGUiOiJydSJ9.kJrFSEUtm4_EoJtAsd4VnrgKmhkQuglMC14eFbfvwvec5PKxj63WHl6NlLWkVxXXU_m5A_3k8_M818RJN-pFRddqX-XxJ2eDIomOmwmmRQnaOunWOa5RkzQOHOo2jrdQCpyR8Mf_gz_YdPac1AWhUaacXzw8l7Go4bFTxRNUt2U1kyBmzCWsfgNKBHZWaVUoVEL_BcP-57QsY5FAVI78QLzoqeW-W4Yjd4rTMfi9C2kr1N5jCqK4j5U2sFYIKRCUWg4kwUAJU1Xe_Ts48YDNE0MWHHMZc8X_-dWtRkLkTaFhjMh6bwvTXOHS4cHhZw71Uc0BPOgCNtroSf-xl49jyQ',
                  'refresh_token': '1/a2Vc4DEaoHG9PtAcAxRja4MHONN6bcIfblWUIzeHHsUMEudVrK5jSpoR30zcRFq6',
                  'token_type': 'Bearer',
                  'access_token': 'ya29.CjHhAtYXDhrurj5115SifsCNFXeswkrFM1J4v4iANF2vgJXI3qcMYtB3WgClPD3tHZ7P',
                  'expires_in': 3600}
    return registration_gplus(visual_res)
    # on real
    get_user_code = requests.get(url='https://accounts.google.com/o/oauth2/auth',
                                 params={'client_id': CLIENT_ID_for_gplus,
                                         'redirect_uri': REDIRECT_URI_for_gplus,
                                         'scope':'https://www.googleapis.com/auth/userinfo.profile',
                                         'response_type':'code',
                                         'approval_prompt': 'force',
                                         'access_type': 'offline'})
    request_status = get_user_code.status_code
    if request_status == 200:
        return redirect(get_user_code.url)
    else:
        return get_user_code.content, request_status


@view_auth.route('/get_access_token_gplus', methods=['GET'])
def get_access_token_gplus():
    code = request.args.get('code')
    get_access_token = requests.post(url='https://www.googleapis.com/oauth2/v4/token',
                                    params={'client_id': CLIENT_ID_for_gplus,
                                            'client_secret': CLIENT_SECRET_for_gplus,
                                            'redirect_uri': REDIRECT_URI_for_gplus,
                                            'code': code,
                                            'grant_type': 'authorization_code'})
    request_status = get_access_token.status_code
    if request_status != 200:
        return get_access_token.content, request_status

    access_dict = json.loads(get_access_token.text)
    return registration_gplus(access_dict)


def registration_gplus(access_dict):
    client_dict = jwt.decode(access_dict['id_token'], verify=False)

    session['logged_user'] = True
    session['user_name'] = client_dict.get('given_name') + ' ' + \
                           client_dict.get('family_name')
    session['photo'] = client_dict.get('picture')
    auth_user_id = client_dict.get('sub')
    client_portal = 'google.com'

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

    return redirect(url_for('view_auth.show_notes', user_id=session.get('user_id')))
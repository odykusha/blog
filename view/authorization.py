import requests, json, jwt

from flask import session, redirect, url_for, request, Blueprint, abort

from view.db_utils import get_db
from app_tools import sql_scripts


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


view_auth = Blueprint('view_auth', __name__)
###############################################################################
# auth API VK.com
###############################################################################
# VK
@view_auth.route('/auth_vk', methods=['GET'])
def auth_vk():
    if session.get('logged_user'):
        return redirect(url_for('view_notes.show_notes'))
    # on local
    # visual_res = {"access_token":"9d4ed75bbf948ff4d835f9e99fc6bdd05781a927c29a80cb4ad46c2d4770816b1c24f9c0ee27d8eef167d","expires_in":86390,"user_id":137375300}
    # return registration_vk(visual_res)
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
        if cr['status']:
            session['logged_user'] = True
            session['user_id'] = cr['id']
            if cr['is_admin']:
                session['logged_admin'] = True
        else:
            session.pop('photo', None)
            session.pop('user_name', None)
            abort(403)

    return redirect(url_for('view_notes.show_notes', user_id=session.get('user_id')))


###############################################################################
# auth API Google+
###############################################################################
# Google+
@view_auth.route('/auth_gplus', methods=['GET'])
def auth_gplus():
    if session.get('logged_user'):
        return redirect(url_for('view_notes.show_notes'))
    # on local
    # visual_res = {'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImU3ZGJmNTI2ZjYzOWMyMTRjZDc3YjM5NmVjYjlkN2Y4MWQ0N2IzODIifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdF9oYXNoIjoiODJMejZvWnY1MEtaWVBONElMMDJKZyIsImF1ZCI6IjY3ODk3MTEzNDAwNS1wMDR1OHAzaXE4dHQ2dGg4MW45aTVicTE1aTdtYTg1MS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwNDMwMjI3MDk3MDYwMjI3OTc2NSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhenAiOiI2Nzg5NzExMzQwMDUtcDA0dThwM2lxOHR0NnRoODFuOWk1YnExNWk3bWE4NTEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJoZCI6InNtYXJ0d2ViLmNvbS51YSIsImVtYWlsIjoiby5kaWt1c2hhQHNtYXJ0d2ViLmNvbS51YSIsImlhdCI6MTQ2MzE1MTAyMywiZXhwIjoxNDYzMTU0NjIzLCJuYW1lIjoi0J7Qu9C10LMg0JTQuNC60YPRiNCwIiwicGljdHVyZSI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tTHhmUVNjTkx5MDgvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQk0vbmhEaEVtYVY5encvczk2LWMvcGhvdG8uanBnIiwiZ2l2ZW5fbmFtZSI6ItCe0LvQtdCzIiwiZmFtaWx5X25hbWUiOiLQlNC40LrRg9GI0LAiLCJsb2NhbGUiOiJydSJ9.kJrFSEUtm4_EoJtAsd4VnrgKmhkQuglMC14eFbfvwvec5PKxj63WHl6NlLWkVxXXU_m5A_3k8_M818RJN-pFRddqX-XxJ2eDIomOmwmmRQnaOunWOa5RkzQOHOo2jrdQCpyR8Mf_gz_YdPac1AWhUaacXzw8l7Go4bFTxRNUt2U1kyBmzCWsfgNKBHZWaVUoVEL_BcP-57QsY5FAVI78QLzoqeW-W4Yjd4rTMfi9C2kr1N5jCqK4j5U2sFYIKRCUWg4kwUAJU1Xe_Ts48YDNE0MWHHMZc8X_-dWtRkLkTaFhjMh6bwvTXOHS4cHhZw71Uc0BPOgCNtroSf-xl49jyQ',
    #               'refresh_token': '1/a2Vc4DEaoHG9PtAcAxRja4MHONN6bcIfblWUIzeHHsUMEudVrK5jSpoR30zcRFq6',
    #               'token_type': 'Bearer',
    #               'access_token': 'ya29.CjHhAtYXDhrurj5115SifsCNFXeswkrFM1J4v4iANF2vgJXI3qcMYtB3WgClPD3tHZ7P',
    #               'expires_in': 3600}
    # return registration_gplus(visual_res)

    # on real
    outh2_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        'response_type=code&'
        'client_id={client_id}&'
        'scope=openid%20email%20profile&'
        'redirect_uri={redirect_uri}'.format(
            client_id=CLIENT_ID_for_gplus,
            redirect_uri=REDIRECT_URI_for_gplus,
        )
    )
    return redirect(outh2_url)


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
        if cr['status']:
            session['logged_user'] = True
            session['user_id'] = cr['id']
            if cr['is_admin']:
                session['logged_admin'] = True
        else:
            session.pop('photo', None)
            session.pop('user_name', None)
            abort(403)

    return redirect(url_for('view_notes.show_notes', user_id=session.get('user_id')))


###############################################################################
@view_auth.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_user', None)
    session.pop('logged_admin', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    session.pop('photo', None)
    return redirect(url_for('view_notes.show_notes'))
import functools
import random
import sqlite3


from flask import session, redirect, url_for, render_template, request, jsonify, Blueprint, abort

from view import app
from view.forms import RandForm
from view.db_utils import get_db
from app_tools import note_filter, sql_scripts

view_rand = Blueprint('view_rand', __name__)


###############################################################################
# randomizer
###############################################################################
@view_rand.route('/rand', methods=['GET'])
def rand_show():
    if not session.get('logged_admin'):
        return abort(404)

    form = RandForm()
    db = get_db()
    views = db.execute(sql_scripts.get_rand).fetchall()[0]
    form.first_text.data = views['first']
    form.second_text.data = views['second']
    form.other_text.data = views['other']

    return render_template(
        'rand.html',
        form=form
    )


@view_rand.route('/rand/save', methods=['POST'])
def ajax_rand_save():
    if not session.get('logged_admin'):
        return abort(404)

    first_text  = request.form['first_text']
    second_text = request.form['second_text']
    other_text  = request.form['other_text']

    form = RandForm()
    db = get_db()

    if form.save():
        db.execute(sql_scripts.change_rand,
                   [first_text, second_text, other_text])
        try:
            db.commit()
        except sqlite3.OperationalError:
            return jsonify(status='ERR', message='якесь гівно блочить базу')
        return jsonify(status='OK', message='Зміни збережено')
    # по невідомим причинам
    return jsonify(status='ERR', message='я хз чому так вийшло')


@view_rand.route('/rand/get', methods=['POST'])
def ajax_rand_get():
    if not session.get('logged_admin'):
        return abort(404)

    first_text = request.form['first_text']
    second_text = request.form['second_text']
    other_text = request.form['other_text']
    selected_first = request.form['selected_first']
    selected_second = request.form['selected_second']
    selected_other = request.form['selected_other']

    if selected_first == 'true':
        role = 'first'
        rand_list = first_text.split(',') + other_text.split(',')
    elif selected_second == 'true':
        role = 'second'
        rand_list = second_text.split(',') + other_text.split(',')
    elif selected_other == 'true':
        role = 'other'
        rand_list = first_text.split(',') + second_text.split(',') + other_text.split(',')
    rand = random.choice(rand_list)

    form = RandForm()
    if form.go_rand():
        return jsonify(status='OK', message=role + ': ' + rand)
    # по невідомим причинам
    return jsonify(status='ERR', message='я хз чому так вийшло')

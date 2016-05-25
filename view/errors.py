from flask import render_template, Blueprint, url_for


view_errors = Blueprint('view_errors', __name__)
###############################################################################
# error
###############################################################################
@view_errors.app_errorhandler(403)
def err403(error):
    message = '<img src=' + url_for('static', filename='img/noway.png') + '> <br>'
    message += "Твій обліковий запис заблоковано!<br> " + str(error)
    return render_template('error.html', error_message=message), 403


@view_errors.app_errorhandler(404)
def err404(error):
    message = "Шукаєш те, чого немає!<br> " + str(error)
    return render_template('error.html', error_message=message), 404


@view_errors.app_errorhandler(405)
def err405(error):
    message = "Такий метод не підтримується!<br> " + str(error)
    return render_template('error.html', error_message=message), 405

@view_errors.app_errorhandler(418)
def err418(error):
    message = "Я чайник, я не знаю як це реалізувати<br> " + str(error)
    return render_template('error.html', error_message=message), 418

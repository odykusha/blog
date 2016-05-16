from flask import render_template, Blueprint


view_errors = Blueprint('view_errors', __name__)
###############################################################################
# error
###############################################################################
@view_errors.app_errorhandler(403)
def err403(error):
    message = "У вас немає прав для перегляду записів інших користувачів!<br> " + str(error)
    return render_template('error.html', error_message=message), 403


@view_errors.app_errorhandler(404)
def err404(error):
    message = "Шукаєш те, чого немає!<br> " + str(error)
    return render_template('error.html', error_message=message), 404


@view_errors.app_errorhandler(405)
def err405(error):
    message = "Такий метод не підтримується!<br> " + str(error)
    return render_template('error.html', error_message=message), 405
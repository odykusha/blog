import os

from view import app
from view.authorization import view_auth
from view.errors import view_errors
from view.notes import view_notes
from view.randomizer import view_rand


###############################################################################
# Configuration
###############################################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')
DEBUG = True
SECRET_KEY = os.urandom(25)
CSRF_ENABLED = True
HOST = '0.0.0.0'
PORT = 8080
MAX_NOTES_ON_PAGE = 10
MAX_USERS_ON_PAGE = 20

# cache = Cache(app,config={'CACHE_TYPE': 'simple'})
# tools = DebugToolbarExtension(app)
app.config.from_object(__name__)
app.root_path = os.path.dirname(os.path.abspath(__file__))
app.register_blueprint(view_auth)
app.register_blueprint(view_errors)
app.register_blueprint(view_notes)
app.register_blueprint(view_rand)


###############################################################################
if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
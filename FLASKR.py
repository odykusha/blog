from view import app
from view.authorization import view_auth
import os

from flask import g
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

# cache = Cache(app,config={'CACHE_TYPE': 'simple'})
# tools = DebugToolbarExtension(app)
app.config.from_object(__name__)
app.register_blueprint(view_auth)

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


###############################################################################
if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
# -*- coding: utf-8 -*-
import sqlite3, os


from view.db_utils import init_db
from time import sleep

# print('start init DB')
# init_db()
# print('DB create')
# sleep(1)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flaskr.db')

def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv

db = connect_db()

print('start')
for i in range(100, 201):
    db.execute('insert into users (client_id, portal, user_name, photo) values (?, ?, ?, ?)',
               ['clientID_'+str(i),
                'portal_'+str(i),
                'user_name_'+str(i),
                'photo_'+str(i)])
db.commit()
print('stop')

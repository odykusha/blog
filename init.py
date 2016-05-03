# -*- coding: utf-8 -*-
from FLASKR import init_db, connect_db
from time import sleep

# print('start init DB')
# init_db()
# print('DB create')
# sleep(1)

# db = connect_db()
#
# for i in range(101, 201):
#     db.execute('insert into notes (text, user_id, global_visible) values (?, ?, ?)',
#                ['text'+str(i),
#                 'user'+str(i),
#                 1])
# db.commit()
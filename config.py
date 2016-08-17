#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

import os
import json

from Siberia.data import ProxyStack

config = ProxyStack(
        basedir=os.path.split(os.path.abspath(__file__))[0],
        templates_path=['templates/'],
        static_path='static/',
        debug=True,
        hostname='0.0.0.0',
        port=3001,
        email="root@localhost",
        cookies=ProxyStack(
                cookie_salt="somesaltforcookie",
                cookie_name="_ids_syberia_cook",
                cookie_expired=864000 * 30,
                cookie_domain='localhost',
                cookie_value=None,
                session_time=3,
        ),
        database=ProxyStack(
                host='localhost',
                db='blog',
                user='anonymous',
                password='anonymous',
                port=3306
        ),
        errors=ProxyStack({
            '404': 'errors/404.html',
            '403': 'errors/403.html',
            '405': 'errors/405.html',
        }),
        defaultroot=ProxyStack(
                name='root',
                mail='root@localhost',
                password='root',
                role='root',
        ),
        adminka=ProxyStack(
                routepath='/admpanel',
        ),
       role=ProxyStack(
                root="root",
                admin="admin",
                user="user",
                anonymous="anonymous",
        ),
        perm=ProxyStack(
                root=ProxyStack(read=True, write=True, delete=True, edit=True),
                admin=ProxyStack(read=True, write=True, edit=True, delete=False),
                user=ProxyStack(read=True, write=True, edit=False, delete=False),
                anonymous=ProxyStack(read=True, write=False, edit=False, delete=False),
        ),
        database_sqlite=ProxyStack(
                engine='playhouse.sqlite_ext.SqliteExtDatabase',
                name='blog.dbs',
                pragmas=(('synchronous', 0), ('journal_mode', 'WAL')),
        ),
        database_mysql=ProxyStack(
                host='localhost',
                db='blog',
                user='anonymous',
                password='anonymous',
                port=3306
        ),
        database_psql=ProxyStack(
                database='blog',
                user='anonymous',
                password='anonymous',
                port=5432,
                host='localhost'
        ),

        jinja_filters=ProxyStack(

        ),
        jinja_globals=ProxyStack(
                jloads = json.loads,
                jdumps = json.dumps,
                dict=dict,
                type=type,
                str=str,
        ),
        login_restore=ProxyStack(
                _from =None,
                _to=None,
                _subject="Восстановление забытого пароля",
                _body="""<html><h3>Восстановление забытого пароля <hr/>
                 Ваш пароль в системе: <strong>{}</strong> <br>
                 <hr/>
                </html>
                """,
        ),
        pagination=ProxyStack(
                count_on_page=7,
        ),


)

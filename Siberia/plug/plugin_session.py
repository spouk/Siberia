#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'
__all__ = ("SessionPlugin",)
# ---------------------------------------------------------------------------
#   global import
# ---------------------------------------------------------------------------
from ..data import ProxyStack
from ..plugins import SiberiaPlugin
from ..loggers import MetaLogger
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from aiohttp import web
from hashlib import sha224
import uuid
import random
import asyncio
from datetime import datetime
from datetime import timedelta


# ---------------------------------------------------------------------------
#   exception
# ---------------------------------------------------------------------------
class SiberiaSessionPluginException(Exception):
    pass


class SiberiaSessionPluginDatabaseHandlerNotFound(SiberiaSessionPluginException):
    pass


# ---------------------------------------------------------------------------
#   session plugin
# ---------------------------------------------------------------------------
class SessionPlugin(SiberiaPlugin):
    # decorator
    dbwrapper = None

    # plugin definitions variables
    plugin_stack = ProxyStack(
            api=0.1,
            name="Session",
            version=0.1,
            middleware=True,
    )
    # картуины требующие запуска переда стартом сервера
    before_stack = ProxyStack()

    # config for session
    config = ProxyStack(
            logmark='[SESSIONPLUGIN]: {}',

            default_session_time=5,
            default_cookie_name='cookie_session_siberia',
            default_cookie_expired=864000 * 30,
            default_cookie_domain='localhost',
            default_cookie_value=None,

            cookie_salt=None,
            cookie_name=None,
            cookie_expired=None,
            cookie_domain=None,
            cookie_value=None,
            session_time=None
    )

    def __init__(self, app, db=None, cook_table=None, user_table=None):
        self.app = app
        self.current_cookie = None
        self.app.current_cookie = self.current_cookie
        self._check_config_app()

        # # database connector - engine
        # self.db = self.app.database

        # database table for access 'cook' and 'user'
        self.cook_table = cook_table
        self.user_table = user_table
        self.log_status = hasattr(self.app, 'log')
        # info client connect current
        self.client = ProxyStack(host=None, port=None)

        self.sessionstack = ProxyStack()
        self.app.fn.online = self.sessionstack

    @property
    def db(self):
        return self.app.database

    def _check_config_app(self):
        self.config.session_time = self.app.c.cookies.session_time or self.config.default_session_time
        self.config.cookie_name = self.app.c.cookies.cookie_name or self.config.default_cookie_name
        self.config.cookie_expired = self.app.c.cookies.cookie_expired or self.config.default_cookie_expired
        self.config.cookie_domain = self.app.c.cookies.cookie_domain or self.config.default_cookie_domain
        self.config.cookie_value = self.app.c.cookies.cookie_value or self.config.default_cookie_value

    def setup(self):
        self.app.middlewares.append(self.session_middle(app=self.app))

    async def generate_cookie(self):
        return sha224((str(uuid.uuid4()) + str(random.gammavariate(1, 200))).encode()).hexdigest()

    def clientinfo(self, request):
        return request.transport.get_extra_info('peername') or None

    def showsessionstack(self):
        if self.log_status and self.app.c.debuger:
            self.app.log.warning(self.config.logmark.format("{!s}".format(self.sessionstack)))
        print(self.config.logmark.format("{!s}".format(self.sessionstack)))

    @asyncio.coroutine
    def update_status(self, cook, request, conn):
        """обновляет информацию по кукису - статус, время последнего подключения, хост и хидеры"""

        dbs = self.cook_table
        record = yield from (yield from (conn.execute(self.cook_table.select().where(dbs.c.cookie == cook)))).fetchone()
        if record:
            if record.status:
                fq = dict(lastconnect=datetime.today(), host=json.dumps(dict(request.headers.items())), lastip=str(self.client), )
            else:
                fq = dict(status=1, count_connection=record.count_connection + 1, lastconnect=datetime.today(), host=json.dumps(dict(request.headers.items())), lastip=str(self.client), )

            yield from conn.execute(dbs.update().where(dbs.c.id == record.id).values(**fq))

            if self.log_status and self.app.c.debuger:
                self.app.log.info(self.config.logmark.format("=== запись в базе о входящем кукисе успешно обновлена ==="))

    @asyncio.coroutine
    def insert_record(self, cook, request, conn):
        """создает новую запись в таблице кукисов"""

        dbs = self.cook_table
        # формируем запрос на создание новой записи
        q = dbs.insert().values(
                cookie=cook,
                host=json.dumps(dict(request.headers.items())),
                create=datetime.today(),
                status=1,
                lastconnect=datetime.today(),
                lastip="{}:{}".format(self.client.host, self.client.port),
                count_connection=1,
                userid=-1,
        )
        yield from conn.execute(q)

    @asyncio.coroutine
    def db_check_cook(self, cook, request):
        sessionobj = None
        exist_session = self.sessionstack.get(cook, None)

        with (yield from self.db) as conn:
            tr = yield from conn.begin()

            yield from self.check_user_online(conn, request)

            if exist_session:
                self.current_cookie = cook
                yield from self.update_status(cook=cook, request=request, conn=conn)
                sessionobj = exist_session

            else:

                sessionobj = Session(app=self.app, cook=cook)

                dbs = self.cook_table
                resp = yield from conn.execute(self.cook_table.select().where(dbs.c.cookie == cook))
                record = yield from resp.fetchone()
                if record:
                    yield from self.update_status(cook=cook, request=request, conn=conn)
                    self.current_cookie = cook
                else:
                    self.current_cookie = yield from self.generate_cookie()
                    sessionobj.cook = self.current_cookie
                    yield from self.insert_record(cook=self.current_cookie, request=request, conn=conn)

                    if self.log_status and self.app.c.debuger:
                        self.app.log.warning(self.config.logmark.format("===  в таблице кукис: {} не найден ===".format(cook)))
                        self.app.log.info(self.config.logmark.format("=== новая запись в таблице с куками успешно создана ==="))

            yield from tr.commit()
            return sessionobj

    @asyncio.coroutine
    def check_user_online(self, conn, request=None):

        dbs = self.cook_table
        online = yield from(yield from conn.execute(dbs.select().where(dbs.c.status == 1))).fetchall()
        realonline = [x for x in online if (x.lastconnect + timedelta(minutes=self.config.session_time)) < datetime.now()]

        if realonline:
            for x in online:

                if x.cookie in self.sessionstack:
                    sess = self.sessionstack.pop(x.cookie)
                    yield from sess.save()
                    q = dbs.update(). \
                        where(dbs.c.id == x.id).values(status=0, dump_session=sess.savebox)
                else:
                    q = dbs.update(). \
                        where(dbs.c.id == x.id).values(status=0)

                yield from conn.execute(q)

        if self.log_status and self.app.c.debuger:
            self.app.log.info(self.config.logmark.format("=== истекшие сессии почищены ==="))

    def session_middle(self, app):
        """ middleware session """

        @asyncio.coroutine
        def fabrica_session(app, handler):
            @asyncio.coroutine
            def middleware(request):
                # сохраняем текущий запрос в общую область видимости приложения
                self.app.request = request

                # info client connecter
                host, port = self.clientinfo(request)
                self.client.port = port
                self.client.host = host
                if self.log_status and self.app.c.debuger:
                    self.app.log.info(self.config.logmark.format("входящее соединение ==> {}:{}".format(self.client.host, self.client.port)))

                if self.config.cookie_name in request.cookies:
                    if self.log_status and self.app.c.debuger:
                        self.app.log.info(self.config.logmark.format("=== обнаружен входящий кукис совпадающий с названием нашего домена {} ===".format(
                                request.cookies.get(self.config.cookie_name))))
                        self.app.log.info(self.config.logmark.format("session stack --> {!s}".format(self.sessionstack)))

                cook = request.cookies.get(self.config.cookie_name)
                sessionobj = yield from self.db_check_cook(cook=cook, request=request)
                # сохраняем  сессию в стаке сессий если там есть место
                self.sessionstack.update({self.current_cookie: sessionobj})
                # добавление объекта сессии к разным инстансам
                self.app.session = sessionobj
                request.session = sessionobj
                # формируем ответ из запроса предварительно, для установки кука нового если потребуется
                response = yield from handler(request)
                if isinstance(response, web.Response):
                    response.set_cookie(name=self.config.cookie_name,
                                        value=self.current_cookie,
                                        expires=self.config.cookie_expired)

                return response

            return middleware

        return fabrica_session


# ---------------------------------------------------------------------------
#   Session for spouk async blog
# ---------------------------------------------------------------------------
class Session(ProxyStack):
    """session for spouk async blog application"""

    def __init__(self, app, cook, **kwargs):
        self.app = app
        self.cook = cook
        self.savebox = None

    async def save(self):
        """сохранения значений Box текущей сессии в self.savebox
        для дальнейшего сохранения в базе данных"""
        # в лямбде `isinstance` не работает корректно, хуй знает почему :/, а может и не знает :)
        checker = lambda obj: {k: v for k, v in obj.items() if type(v) in (list, dict, str, int, float, bool, None, ProxyStack) if k != 'savebox'}
        obj = checker(self)
        {obj.update({k: checker(v)}) for k, v in obj.items() if isinstance(v, dict)}
        self.savebox = json.dumps(obj)
        return self.savebox

    async def load(self, savebox):
        """загрузка сохранной в базе данных сессии в объект типа Box"""
        if isinstance(savebox, (str)):
            result = json.loads(dict(savebox))
            self.update(dict(result))


# ---------------------------------------------------------------------------
#   Validator variables to correct save json format from/to session
# ---------------------------------------------------------------------------
class Validator:
    __doc__ = """класс-валидатор для проверки валидных с позиции json формата
    для сохранения/загрузки в базу данных, отсев функций и прочего треша"""

    def __init__(self, items=None):
        self.items = items
        self.result = None
        self._validatetypes = (str, int, dict, tuple, float, list, bool, bytes, ProxyStack)

    async def __checktype(self, item):
        return (isinstance(item, self._validatetypes) or (item is None)) or False

    async def valid(self, items=None):
        """сортировка по типу и соответственной рекурсии"""
        if items:
            self.items = items
        if self.items:
            if isinstance(self.items, dict):
                self.result = await self.dict_valid(self.items)
            if isinstance(self.items, list):
                self.result = await self.list_valid(self.items)
            if isinstance(self.items, tuple):
                self.result = await self.tuple_valid(self.items)
        return self.result

    async def dict_valid(self, items, fold=None, flag=False):
        """букварь - рекурсивный отсев не соответствующих списку типов"""
        use_items = items
        save = fold or {}
        if flag:
            return save
        if isinstance(use_items, dict):
            k = None
            v = None
            try:
                k, v = use_items.popitem()
            except KeyError:
                flag = True
            if self.__checktype(v):
                save.update({k: v})
            if isinstance(v, dict):
                save.update(self.dict_valid(v))
            if isinstance(v, list):
                save.update({k: self.list_valid(v)})
            if isinstance(v, tuple):
                save.update({k: self.tuple_valid(v)})
            return await self.dict_valid(use_items, fold=save, flag=flag)

    async def list_valid(self, items, fold=None, flag=False):
        """списки - рекурсивный отсев не соответствующих списку типов"""
        use_items = items
        save = fold or []
        if flag:
            return save

        if isinstance(items, list):
            x = None
            try:
                x = use_items.pop()
            except IndexError:
                flag = True
            if isinstance(x, self.__validate_types):
                save.append(x)
            if isinstance(x, list):
                save.append(self.list_valid(x))
            if isinstance(x, dict):
                save.append(self.dict_valid(x))
            if isinstance(x, tuple):
                save.append(self.tuple_valid(x))
            return await self.list_valid(use_items, fold=save, flag=flag)

    async def tuple_valid(self, items, fold=None, flag=False, index=0):
        """кортеж - рекурсивный отсев не соответствующих списку типов"""
        if fold is None:
            save = []
            flag = True
            index = len(items) - 1
        else:
            save = fold
            index = index

        if index < 0:
            return tuple(save)

        if isinstance(items, tuple):
            x = items[index]
        if self.__checktype(x):
            save.append(x)
        if isinstance(x, tuple):
            save.append(self.tuple_valid(x))
        if isinstance(x, list):
            save.append(self.list_valid(x))
        if isinstance(x, dict):
            save.append(self.dict_valid(x))
        index -= 1
        return await self.tuple_valid(items, fold=save, index=index)

# ---------------------------------------------------------------------------
#   example table need for good work session plugin
# ---------------------------------------------------------------------------

# # куки сессий
# cook  = sa.Table('blog_cook', metadata,
#                  sa.Column('id', sa.Integer, primary_key=True),
#                  sa.Column('cookie', sa.String()),
#                  sa.Column('host', sa.String()),
#                  sa.Column('create', sa.DateTime(), default=datetime.today()),
#                  sa.Column('dump_session', sa.String()),
#                  sa.Column('status', sa.SmallInteger()),
#                  sa.Column('lastconnect', sa.DateTime(),default=datetime.today()),
#                  sa.Column('lastip', sa.String()),
#                  sa.Column('count_connection', sa.Integer()),
#                  sa.Column('userid', sa.Integer()),
#                  )

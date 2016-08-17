#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

import asyncio
from aiohttp import Request, request
from aiohttp.web import Route
from functools import wraps
from Siberia.data import ProxyStack


# декоратор для базы данных
def decdb(f):
    @wraps(f)
    @asyncio.coroutine
    def wrap(self, *args, **kwargs):
        with (yield from self.app.database) as conn:
            result = None
            tr = yield from conn.begin()
            try:
                result = yield from f(self, conn=conn, *args, **kwargs)
                yield from tr.commit()
            except Exception as error:
                print("FUCKEN ERROR:", error, f)
                # yield from tr.rollback()
                if self.log_status and self.app.c.debuger:
                    self.app.log.info(self.config.logmark.format(
                            "[DATABASE_ERROR] [db_wrapper][rollback] {!s}".format(error)))
            return result
    return wrap

import inspect

# декоратор для базы данных 2
def decdbrock(app=None):
    def decdb2(f):
        @asyncio.coroutine
        def wrap(*args, **kwargs):
            # print("Function: ", f, inspect.iscoroutinefunction(f), inspect.iscoroutine(f), inspect.isawaitable(f) )
            with (yield from app.database) as conn:
                result = None
                tr = yield from conn.begin()
                try:
                    result = yield from f(conn=conn, *args, **kwargs)
                    yield from tr.commit()
                except Exception as error:
                    print("[decdbrock] FUCKEN ERROR:", error, f)
                    # yield from tr.rollback()
                    if app.log_status and app.app.c.debuger:
                        app.app.log.info(app.config.logmark.format(
                                "[DATABASE_ERROR] [db_wrapper][rollback] {!s}".format(error)))

                return result
        return wrap
    return decdb2

# врапер для шаблонов
def decjin(app=None, adding=dict):
    def djin(page):
        def _decor_render(f):
            async def wrapper(*args, **kw):
                _empty = dict()
                kwargs_func = await f(*args, **kw)
                if inspect.iscoroutine(kwargs_func):
                    return await kwargs_func

                obj, request = len(args) == 2 and args or (None, None)
                _empty.update(dict(obj=obj, request=request))
                (adding and isinstance(adding, dict)) and _empty.update(**adding)
                (kwargs_func and isinstance(kwargs_func, dict)) and _empty.update(**kwargs_func)

                return await app.render(page, **_empty)

            return wrapper

        return _decor_render

    return djin

# проверка на роль и статус онлайн нет
def autorize(app=None, validate_list_roles=()):
    def auth(f):
        async def check_role(*args, **kw):
            # resolve route obj by request
            result = await app.router.resolve(app.request)
            # print("[AUTH]", app.request.query_string, app.request.path, result.__dict__)
            # print("AUTH:", app.request.match_info, app.request.GET)
            # rs = app.request.match_info
            # print("[AUTYH] mathc_info keys: ", rs.keys())
            # print("[AUTYH] mathc_info values: ", rs.values())
            # print("[AUTH] RESULT_route:", result._route, result._route.name)
            app.session.ref = ProxyStack(
                path="http://{}{}".format(app.request.host, app.request.path_qs),
                ref_name=result._route.name,
                parts=dict(app.request.match_info),
                query=dict(app.request.GET)
            )
            app.session.ref.rdy = ProxyStack(
                    route_name=app.session.ref.ref_name,
                    parts=app.session.ref.parts,
                    query=app.session.ref.query,
            )
            kw.update(dict(answer = ProxyStack(flash="")))

            # app.session.ref = "http://{}{}".format(app.request.host, app.request.path_qs)
            app.session.ref_name = result._route.name
            user = app.session.get('user', None)
            if user and user.role in validate_list_roles and user.online:
                return await f(*args, **kw)
            else:
                return await app.fn.redirect('login_get')

        return check_role
    return auth


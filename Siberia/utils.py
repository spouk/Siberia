#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from .exceptions import SiberiaHTTPRouteErrors, SiberiaPluginInvalidType
from .data import ProxyStack
from .plugins import SiberiaPlugin

from aiohttp import web
import aiohttp.web_exceptions as httperrors
import inspect
import asyncio
from mailer import Message, Mailer
from aiohttp.web import DynamicRoute, PlainRoute, StaticRoute
from collections import OrderedDict



class Utils:
    def __init__(self, app):
        self.app = app

    #---------------------------------------------------------------------------
    #   routing utils functions
    #---------------------------------------------------------------------------
    def short_url(self):
        def wrapper(name):
            return self.app.router['{}'.format(name)].url()
        return wrapper

# request.app.router['user-info'].url(
# ...     parts={'user': 'john_doe'},
# ...     query="?a=b")
# '/john_doe/info?a=b'

    def url_for(self, name, parts={}, query={}):
        if name not in self.app.router.named_routes():
            raise SiberiaHTTPRouteErrors("[UTILS] Name route `{}` not found, check `name` routing".format(name))
        result = None
        if parts and query:
            result = self.app.router[name].url(parts=parts, query=query)
            # result = self.app.router['{}'.format(name)].url(parts=parts, query=query)
        elif parts and not query:
            result = self.app.router[name].url(parts=parts)
            # result = self.app.router['{}'.format(name)].url(parts=parts)
        elif not parts and query:
            result = self.app.router[name].url(query=query)
            # result = self.app.router['{}'.format(name)].url(query=query)
        elif not parts and not query:
            result = self.app.router[name].url()
            # result = self.app.router['{}'.format(name)].url()
        return result

    async def redirect(self, route_name, parts=None, query=None):
        """ редирект, если нет такого рутера то редирект на 404 """
        # testiung
        url = None
        errorpage = None
        if route_name in self.app.router.named_routes():
            route_obj = self.app.router[route_name]
            if parts and query:
                url = self.app.router[route_name].url(parts=parts, query=query)
            if parts and not query:
                print(parts)
                url = self.app.router[route_name].url(parts=parts)
            if not parts and not query:
                url = self.app.router[route_name].url()

        else:
            errorpage = await self.app.render(self.app.c.errors['404'])
        return url and web.HTTPFound(url) or errorpage

    @asyncio.coroutine
    def send_email(self, _to, _from, _body,_subject, attach_obj=None, _mailhost=None, debug=False):
        """ отправка мыла """
        mailhost = Mailer(_mailhost and _mailhost or 'localhost')
        message  = Message(From=_from, To=_to, charset='utf-8',)
        message.Subject = _subject
        message.Html = _body
        if attach_obj:
            message.attach(attach_obj)
        mailhost.send(msg=message, debug=debug)

    def getarg(self, key):
        try:
            value = self.app.request.match_info[key]
        except KeyError as err:
            return None
        return value

    # async def abort(self, HTTPCode):
    #     """ редирект по коду """
    #     # check exists default page for errors, if not use defaults
    #     if 'errors' in self.config:
    #         msg = self.config.errors.get('error{}'.format(code), None)
    #         if msg:
    #             return await self.render(msg)
    #         # msg not found use default http message exception
    #     res = self.manager.http_code(code=str(code))
    #     return res() or web.HTTPError()

    def install_plugin(self, plug):
        """ check type plugin """
        if not isinstance(plug, SiberiaPlugin):
            raise SiberiaPluginInvalidType("[UTILS] Wrong type plugin `{}`".format(plug))
        else:
            name = plug.plugin_stack.name.lower()
            self.app.plugins.update({name: plug})
            # load config plug to global application namespace
            self.app.c.plugins.update({name: plug.config})
            # run setup plugin
            plug.setup()

            # update stack before coro
            if hasattr(plug, 'before_stack') and plug.before_stack:
                self.app.before_stack.update(plug.before_stack.items())

    def set_error_page(self, page, http_code, ):
        """устаналивает страницу на код `HTTP` """
        self.app.c.errors[http_code] = page

    def before_run_stack(self):
        async def __runer():
            if self.app.before_stack:
                for name, fn in self.app.before_stack.items():
                    print("-- RUN BEFORE STACK fn:  ", name, fn)
                    await fn()
        self.app.loop.run_until_complete(__runer())

    # ---------------------------------------------------------------------------
    #   debuginf methods
    # ---------------------------------------------------------------------------
    def show_cfg_global(self):
        if hasattr(self, 'log'):
            self.log.info(self.__dict__)
            for k, b in self.config.items():
                self.log.info("{:<30}{!s:<40}".format(k, b))
        else:
            print(self.__dict__)
            for k, b in self.config.items():
                print("{:<30}{!s:<40}".format(k, b))

    def maproute(self):
        """view all routines"""
        # print("{:*^40}\n".format("ROUTES {} {}".format(self.hostname, self.port)))
        if hasattr(self, 'log'):
            for route in self.app.router.routes():
                self.log.info(route)
            self.log.info("Counts: [ {} ] {:*^40}\n".format(len(self.app.router.routes()), "ROUTES END"))
        else:
            for route in self.app.router.routes():
                print(route)
            print("Counts: [ {} ] {:*^40}\n".format(len(self.app.router.routes()), "ROUTES END"))

    # ---------------------------------------------------------------------------
    #   routing decorators
    # ---------------------------------------------------------------------------
    def route(self, path, method='*', name=None, handler=None):
        """decorator for human add routing path"""
        # check args
        method = method or '*'
        if handler:
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return

        def _wrapper(handler):
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return handler
        return _wrapper

    def get(self, path, name=None, handler=None):
        """decorator for human add routing path"""
        method = 'GET'
        if handler:
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return

        def _wrapper(handler):
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return handler
        return _wrapper

    def post(self, path, name=None, handler=None):
        """decorator for human add routing path"""
        method = 'POST'
        if handler:
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return

        def _wrapper(handler):
            self.app.router.add_route(method=method, path=path, handler=handler, name=name)
            return handler
        return _wrapper

    async def route_static(self, prefix, path):
        """add static path"""
        self.app.router.add_static(prefix, path)


#---------------------------------------------------------------------------
#   flash messanger int use
#---------------------------------------------------------------------------
# {group, type, message}
# ex: {adminka, info, "Hello from flasher"}
# f = Flasher()
# f.push(adminka, info, "Hello from flasher") -> save it: {int_key : {group, type, message}, int_key:{group, type, message}}

class Flasher:
    def __init__(self, app):
        self.app=app
        self._stack = OrderedDict()
        self._counter = 0

    def _key(self, value=None):
        if value:
            return ''.join('f' + str(value))
        return ''.join('f' + str(self._counter))

    def send(self, g, t, m):
        """g=group, t=type, m=message"""
        self._stack.update({str(self._counter) : (g, t, m)})
        self._counter += 1

    def get(self):
        if self._stack:
            result = self._stack.pop(str(self._counter - 1), None)
            if result:
                # del self._stack[str(self._counter - 1)]
                if self._counter > 0:
                    self._counter -= 1
            return result
        return None

    def get_g(self,g):
        """get all group"""
        if self._stack:
            st = []
            def _pop(k,v):
                self._stack.pop(k)
                st.append(v)
            l = {k:v for k,v in self._stack.items() if v[0] == g}
            [_pop(k,v) for k,v in l.items()]
            return st
        return []


    def get_t(self,t):
        """get all type"""
        if self._stack:
            st = []
            def _pop(k,v):
                self._stack.pop(k)
                st.append(v)
            l = {k:v for k,v in self._stack.items() if v[1] == t}
            [_pop(k,v) for k,v in l.items()]
            return st
        return []
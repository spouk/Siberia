#!/usr/local/bin/python
__author__ = 'spouk'
__all__ = ('AdminkaPlugin',)
__version__ = 0.1
__name__ = 'AdminkaPLugin for Siberia'
__middleware__ = True
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader, TemplateError
from ..plugins import SiberiaPlugin
from ..data import ProxyStack
from aiohttp import web, request
from asyncio import coroutine
from sqlalchemy import func
import os
#---------------------------------------------------------------------------
#   implement jinja2 plugin for Siberia
#---------------------------------------------------------------------------
class AdminkaPlugin(SiberiaPlugin):
    # stack assert messages
    assert_msg = ProxyStack(
        route = " не найден путь для добавления роутера для админки",
        middle = " не найден стак в основном приложении для middlewares",
        jinja2 = " не найден плагин Jinja2Plugin, установите его, он нужен для работы админки",

    )

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "Adminka",
        version = 0.1,
        middleware = True,
    )

    # config for session
    config = ProxyStack(
        adminroute = '/adminka',
        template_path = 'adminka/',
        static_path = 'static/',
        mark = '[ADMINKAPLUGIN] {}',

    )

    def __init__(self, app, template_path=None, routeadminka=None):
        self.app = app
        self.routeadminka = routeadminka or self.config.adminroute
        self.template_adminka = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.config.template_path)
        # adminka handlers containers
        self.hand = AdminkaHandlers(app=self.app, adminka=self)

        # result functions some
        self.online = None

    def assignrouteadmin(self):
        # assert self.routeadminka, (self.config.mark.format(self.config.assert_msg.get('route')))
        # adding template
        self.app.fn.get(self.routeadminka, name="adminka", handler=self.hand.adminkalogin)
        # adding static paths
        self.staticpath = os.path.join(self.template_adminka, self.config.static_path)
        print("Adding static path: ", self.staticpath)
        self.app.router.add_static(prefix='/adminka/static/css',
                                   path=self.staticpath + '/css',
                                   name='css_admin')
        self.app.router.add_static(prefix='/adminka/static/font',
                                   path=self.staticpath + '/font',
                                   name='font_admin')
        self.app.router.add_static(prefix='/adminka/static/img',
                                   path=self.staticpath + '/img',
                                   name='img_admin')
        self.app.router.add_static(prefix='/adminka/static/js',
                                   path=self.staticpath + '/js',
                                   name='js_admin')
        print("Added static adminka path")
        # self.app.fn.maproute()

    def setup(self):
        # проверка нужных для плагина переменных и плагинов в основном приложении
        # для работы адимнки требуется jinja плагин, ибо все там адаптировано под испоьзование в качестве рендера `нинзю`
        assert hasattr(self.app, 'middlewares'), (self.config.mark.format(self.config.assert_msg.get('middle')))
        assert 'jinja2' in self.app.plugins, (self.config.mark.format(self.config.assert_msg.get('jinja2')))
        # проверки прошли успешно, добавляем в миддлы
        if hasattr(self.app, 'middlewares'):
            self.app.middlewares.append(self.adminka_middleware(app=self.app))
        # устанавливаю директорию темплейтов для админки к лодеру jinja
        jinja2 = self.app.plugins.get('jinja2')
        jinja2.addtemplate(self.template_adminka)
        print("------NEW JINJA TEMPLATES: ", jinja2.config.template_path)
        # добавляю роутер
        print(self.config.mark.format(" добавляю роутер админки"))
        self.assignrouteadmin()
        print(self.config.mark.format(" добавляю роутер админки, добавил вроде"))


    def adminka_middleware(self, app):
        @coroutine
        def adminka(app, handler):
            @coroutine
            def middleware(request):
                if request.path == self.routeadminka:
                    url = request.app.router['adminka'].url()
                    print("ADMINKA PATH FOUND:", url)
                    # return web.HTTPFound(url)
                    # get users online
                r = yield from self.hand.users_online(request)
                self.online = r

                response = yield from handler(request)
                return response
            return middleware
        return adminka

class AdminkaHandlers(ProxyStack):
    def __init__(self, app, adminka):
        self.adminka = adminka # self adminka
        self.app = app
        self.db = self.app.db
        self.render = self.app.render

    # /`adminkaroute`

    async def adminkalogin(self, request):
        # return web.Response(body='/usr/home/spouk/PycharmProjects/Siberia/plug/adminka/adminka.html'.encode())
        return await self.app.render('adminindex.html', online=self.adminka.online)

    @coroutine
    def url_user_online(self, request):
        res = yield from self.app.render('usersonline.html', online=self.adminka.online)
        return res

    # users online
    @coroutine
    def users_online(self, request):
        with (yield from self.db) as conn:
            dbs = self.db.cook
            # q = dbs.select().where([func.count(dbs.c.status)])
            q = dbs.select().where(dbs.c.status == 1)
            resp = yield from conn.execute(q)
            found = yield from resp.fetchall()
            return found












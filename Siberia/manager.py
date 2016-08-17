#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from aiohttp import web
from sqlalchemy import Table
import asyncio
from aiohttp.log import server_logger

from .data import ProxyStack

from .utils import Utils, Flasher

class Manager(object):
    def __init__(self, app, params):
        self.app = app
        self.params = params
        self.fn = Utils(app=self.app)
        self.app.flasher = Flasher(app=app)

        self.config_init()

    def config_init(self):
        # set variables
        self.app.c = self._config_check_file(self.params.get('config', ProxyStack()))
        self.app.fn = self.fn
        self.app.render = self.app_default_render
        self.app.list_tables = self._check_list_tables(ltbles=self.params.get('list_tables', None))
        [self.fn.install_plugin(plug) for plug in self.app.plugins.values()]


    def _config_check_file(self, config_dict):
        c = ProxyStack()
        if isinstance(config_dict, ProxyStack):
            # debug config/default
            c.hostname = config_dict.hostname or 'localhost'
            c.port = config_dict.port or 3000
            c.basedir = config_dict.basedir or None
            c.debuger = config_dict.debug or False
            c.static_path = config_dict.static_path or 'static/'
            c.template_path = config_dict.templates_path or ['templates/',]
            c.database = config_dict.database or ProxyStack()
            c.errors = config_dict.errors or ProxyStack()
            c.defaultroot = config_dict.defaultroot or ProxyStack()
            c.role = config_dict.role or ProxyStack()
            c.perm = config_dict.perm or ProxyStack()
            c.cookies = config_dict.cookies or ProxyStack()
            c.plugins  = ProxyStack()
            c.config = config_dict
            # set static path
            self.app.router.add_static('/static/', c.static_path)

        return c

    async def app_default_render(page, *args, **kwargs):
        """ дфеолтный рендер """
        return web.Response(body=page)

    def _check_list_tables(self, ltbles):
        """ проверка списка таблиц базы данных """
        accept = ProxyStack()
        if ltbles and isinstance(ltbles, dict):
            accept = {k: v for k, v in ltbles.items() if isinstance(v, Table)}
        return accept

    def run_developing(self, hostname=None, port=None):
        """ run http server"""
        hostname = hostname or self.app.c.hostname
        port = port or self.app.c.port

        self.loop = asyncio.get_event_loop()
        self.handler = self.app.make_handler(access_log=server_logger)
        self.server = self.loop.create_server(self.handler, host=hostname,port=port)
        self.server_process = self.loop.run_until_complete(self.server)
        print("[SIBERIA] run server on: [ {}:{} ]\n".format(hostname, port))
        try:
            self.app.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.handler.finish_connections(1.0))
            self.server_process.close()
            self.loop.run_until_complete(self.server_process.wait_closed())
            self.loop.run_until_complete(self.server.finish())
        self.app.loop.close()



#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

__all__ = ['Application']

from .plugins import SiberiaPlugin
from .middlewares import CatcherPlugin
from .data import ProxyStack
from .manager import Manager

from aiohttp import web, request
from sqlalchemy import Table
import aiohttp.web_exceptions as httperr
import inspect
from collections import Sequence
import asyncio

# logging
from . loggers import MetaLogger
from .data import ProxyStack

class Application(web.Application, metaclass=MetaLogger):
    """ init new application """

    def __init__(self, *, logger=web.web_logger, debuger=False, loop=None, router=None, handler_factory=web.RequestHandlerFactory, config=None, debug=False, list_tables=None, **kwargs):
        super().__init__(logger=logger, loop=loop, router=router, handler_factory=handler_factory)

        # configs
        self.params = dict(logger=logger, loop=loop, router=router, handler_factory=handler_factory, config=config, debug=debug, list_tables=list_tables, kwargs=kwargs)
        self.c = None
        self.fn = None
        self.middles = []
        self.list_tables = None
        self.render = None
        self.plugins = ProxyStack(catcher=CatcherPlugin(app=self))
        # self.plugins = ProxyStack()

        # flasher
        self.flasher = None

        # database
        self.database = None

        #before coroutines stack - карутины требующие запуска перед стартом сервера
        self.before_stack = ProxyStack()

        self.debuger = debuger

        # manager
        self.manager = Manager(app=self, params=self.params)

        # run server
        self.run = self.manager.run_developing


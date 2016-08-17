#!/usr/local/bin/python
__author__ = 'spouk'
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from ..exceptions import SiberiaPluginInvalidConfig
from ..plugins import SiberiaPlugin
from ..data import ProxyStack
from aiopg.sa import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Table
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from asyncio import coroutine
from psycopg2 import ProgrammingError
import asyncio
#---------------------------------------------------------------------------
#   Postgress database plugin for Siberia
#---------------------------------------------------------------------------
class PostgressPlugin(SiberiaPlugin):

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "postgress",
        version = 0.1,
        middleware = True,
    )

    # config for session
    config = ProxyStack(
        user=None,
        password=None,
        database=None,
        host=None,
        port=None,
    )

    # variables
    REQ = ('user','host','port','database','password')

    def __init__(self, app, user=None, password=None, port=None, database=None, host=None, disable_check_config=False, models=None, metadata=None):
        self.app = app
        self.app.db = None
        self.app.database_exists = False
        self.disable_check_config = disable_check_config

        # load list_tables for creating
        self.list_tables = hasattr(self.app, 'list_tables') and self.app.list_tables

        # orm database `sqlalchemy` session
        self.db_session = None

        # declarative `style` sqlalchemy make tables and mapping
        # self.base_declarative = base_declarative


        # models list
        self._models = ProxyStack()
        self._check_models(models=models)

        # check if already running then not run
        self.metadata = metadata


        # database setting
        self.config.user = user
        self.config.password = password
        self.config.database = database
        self.config.port = port or 5432
        self.config.host = host or 'localhost'

        # check config
        self._check_config()

    def setup(self):
        # adding middle to application
        if hasattr(self.app, 'middlewares'):
            self.app.middlewares.append(self.postgress_middleware(app=self.app))
        lo = asyncio.get_event_loop()
        lo.run_until_complete(self.make_engine())


    def _check_config(self):
        if self.disable_check_config: return False
        if not len([True for x in self.REQ if x in self.config and self.config[x]]) == len(self.REQ):
            raise SiberiaPluginInvalidConfig("[PostgressPlugin] wrong config values")
        return True

    def _check_models(self, models):
        if models and isinstance(models, dict):
            self._models.update({k:v for k,v in models.items() if isinstance(v, Table) or isinstance(v, DeclarativeMeta)})
        if self.list_tables:
            self._models.update(self.list_tables)

    async def _create_tables_declarative(self, base, engine):
        """ async create table = declarative style"""
        if hasattr(base, 'metadata'):
            base.metadata.create_all(bind=engine, checkfirst=True)
        return

    @coroutine
    def make_engine(self):
        engine = yield from create_engine(user=self.config.user,
                        database=self.config.database,
                        host=self.config.host,
                        port=self.config.port,
                        password=self.config.password,
                        )
        # if tables exists assign with attrib to `db`
        if self._models:
            [object.__setattr__(engine,key, value) for key, value in self._models.items()]

        # if first load application call create tables
        if not hasattr(self.app, 'exists_table_runer') and engine and self.metadata:

            # create table
            if self.app.log and self.app.debuger:
                self.app.log.info("[PostgressPlugin] [ `exists_table_runer` метка существования подключения к базе не найдено, создаю новую]")
            yield from  self._create_tables_classic(metadata=self.metadata, engine=engine)

            # set flag for not running during global session work application
            self.app.exists_table_runer = True
            if self.app.log and self.app.debuger:
                self.app.log.info("[PostgressPlugin] [ таблицы успешно созданы ]")

        self.app.db = engine
        return engine


    @coroutine
    def _create_tables_classic(self, engine, metadata):
        """ async create table = declarative style"""
        if engine and metadata:
            with (yield from engine) as conn:
                for x in self._models.values():
                    try:
                        yield from conn.execute(CreateTable(x))
                    except ProgrammingError as error:
                        if hasattr(self.app, 'log') and self.app.log:
                            if self.app.debug:
                                self.app.log.info("[PostgressPlugin] [ `{}` already exists]".format(x))
                        else:
                            if self.app.debug:
                                print("[PostgressPlugin] [ `{}` already exists]".format(x))
        return

    def postgress_middleware(self, app):
        @coroutine        
        def postgress_database_connector(app, handler):
            @coroutine
            def middleware(request):
                # check exists app .log and .debug
                st_log = False
                if hasattr(self.app, 'log'):
                    st_log = True

                # create db engine
                if self.app.database_exists:
                    if st_log and self.app.debuger:
                        self.app.log.info("[PostgressPlugin] [ Подключение к базе {} уже существует, пропускаю создание нового]".format(self.app.db))
                else:
                    # engine = yield from create_engine(user=self.config.user,
                    #                         database=self.config.database,
                    #                         host=self.config.host,
                    #                         port=self.config.port,
                    #                         password=self.config.password,
                    #                         )
                    #
                    # # if tables exists assign with attrib to `db`
                    # if self._models:
                    #     [object.__setattr__(engine,key, value) for key, value in self._models.items()]
                    #
                    # # if first load application call create tables
                    # if not hasattr(self.app, 'exists_table_runer') and engine and self.metadata:
                    #     # create table
                    #     if st_log and self.app.debuger:
                    #         self.app.log.info("[PostgressPlugin] [ `exists_table_runer` метка существования подключения к базе не найдено, создаю новую]")
                    #     yield from  self._create_tables_classic(metadata=self.metadata, engine=engine)
                    #     # set flag for not running during global session work application
                    #     self.app.exists_table_runer = True
                    #     if st_log and self.app.debuger:
                    #         self.app.log.info("[PostgressPlugin] [ таблицы успешно созданы ]")
                    engine = yield from self.make_engine()

                    # assign database connector to current session and current request
                    request.db = self.app.db = self.db = engine
                    self.app.database_exists = True

                    # make tables if not exists (async)
                    # if self.base_declarative and self.db_session:
                    #     yield from self._create_tables(base=self.base_declarative, engine=self.db_session)

                    # TODO[spouk-20.12.15]- запуск из models.некий класс собирающий все методы и присваивающий их всем таблицам
                    # [object.__setattr__(engine,key, value) for key, value in tables.items()]

                response = yield from handler(request)
                return response
            return middleware
        return postgress_database_connector
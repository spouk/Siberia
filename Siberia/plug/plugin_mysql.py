#!/usr/local/bin/python
__author__ = 'spouk'
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from ..exceptions import SiberiaPluginInvalidConfig
from ..plugins import SiberiaPlugin
from ..data import ProxyStack
from aiomysql.sa import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Table
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from asyncio import coroutine
from aiomysql import ProgrammingError, OperationalError, InternalError, IntegrityError
import asyncio

#---------------------------------------------------------------------------
#   Postgress database plugin for Siberia
#---------------------------------------------------------------------------
class MysqlPlugin(SiberiaPlugin):

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "mysql",
        version = 0.1,
        middleware = True,
    )

    # картуины требующие запуска переда стартом сервера
    before_stack = ProxyStack()

    # config for session
    config = ProxyStack(
        user=None,
        password=None,
        db=None,
        host=None,
        port=None,
    )

    # variables
    REQ = ('user','host','port','db','password')

    def __init__(self, app, user=None, password=None, port=None, db=None, host=None, disable_check_config=False, models=None, metadata=None):
        self.app = app
        self.app.database = None
        self.app.database_exists = False
        self.disable_check_config = disable_check_config

        # orm database `sqlalchemy` session
        self.db_session = None

        # models list
        self._models = ProxyStack()
        self._check_models(models=models)

        # check if already running then not run
        self.metadata = metadata

        # database setting
        self.config.user = user
        self.config.password = password
        self.config.db = db
        self.config.port = port or 3306
        self.config.host = host or 'localhost'

        # check config
        self._check_config()

        self.engine = None

    def __runer(self):
        self.app.loop.run_until_complete(self.make_engine(create_table_force=True, debug=self.app.debuger))

    def setup(self):
        self.app.middlewares.append(self.mysql_middleware(app=self.app))
        self.__runer()
        # self.before_stack.update({'mysql_engine': self.make_engine})

    def _check_config(self):
        if self.disable_check_config: return False
        if not len([True for x in self.REQ if x in self.config and self.config[x]]) == len(self.REQ):
            raise SiberiaPluginInvalidConfig("[MysqlPlugin] wrong config values")
        return True

    def _check_models(self, models):
        if models and isinstance(models, dict):
            self._models.update({k:v for k,v in models.items() if isinstance(v, Table) or isinstance(v, DeclarativeMeta)})
        if self.app.list_tables:
            self._models.update(self.app.list_tables)

    async def _create_tables_declarative(self, base, engine):
        """ async create table = declarative style"""
        if hasattr(base, 'metadata'):
            base.metadata.create_all(bind=engine, checkfirst=True)
        return

    @coroutine
    def make_engine(self, create_table_force=False, debug=False):
        engine = yield from create_engine(user=self.config.user,
                        db=self.config.db,
                        host=self.config.host,
                        port=self.config.port,
                        password=self.config.password,
                        )
        # if tables exists assign with attrib to `db`
        if self._models:
            [object.__setattr__(engine,key, value) for key, value in self._models.items()]

        # if first load application call create tables
        if not hasattr(self.app, 'exists_table_runer') or create_table_force:
            if engine and self.metadata:
                # create table
                if self.app.log and self.app.debug:
                    self.app.log.info("[MysqlPlugin] [ `exists_table_runer` метка существования подключения к базе не найдено, создаю новую]")
                yield from self._create_tables_classic(metadata=self.metadata, engine=engine, debug=debug)

                # set flag for not running during global session work application
                self.app.exists_table_runer = True
                if self.app.log and self.app.debug:
                    self.app.log.info("[MysqlPlugin] [ таблицы успешно созданы ]")

            else:

                # set flag for not running during global session work application
                self.app.exists_table_runer = False
                if self.app.log and self.app.debug:
                    self.app.log.info("[MysqlPlugin] [ ошибка при создании таблиц - отсутствует `engine` или/и `metadata` ]")

        self.engine = engine
        self.app.database = self.engine
        return engine

    @coroutine
    def _create_tables_classic(self, engine, metadata, debug=False):
        """ async create table = declarative style"""
        if engine and metadata:
            with (yield from engine) as conn:
                print("SELF._MODELS>VALIES", self._models.values())
                for x in self._models.values():
                    try:
                        yield from conn.execute(CreateTable(x))
                    except (InternalError, ProgrammingError, IntegrityError) as error:
                        if debug:
                            print("ERROR-->", error)
                        if hasattr(self.app, 'log') and self.app.log:
                            if self.app.debug:
                                self.app.log.info("[MysqlPlugin] [ `{}` already exists]".format(x))
                        else:
                            if self.app.debug:
                                print("[MysqlPlugin] [ `{}` already exists]".format(x))
        return

    def mysql_middleware(self, app):
        @coroutine
        def mysql_database_connector(app, handler):
            @coroutine
            def middleware(request):
                # check exists app .log and .debug
                st_log = False
                if hasattr(self.app, 'log'):
                    st_log = True

                # create db engine
                if self.app.database_exists:
                    if st_log and self.app.debug:
                        self.app.log.info("[MysqlPlugin] [ Подключение к базе {} уже существует, пропускаю создание нового]".format(self.app.db))

                # if False:
                #     pass
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
                    self.engine = yield from self.make_engine()

                    # assign database connector to current session and current request
                    self.app.database = self.engine
                    request.db = self.engine
                    self.db = self.engine
                    self.app.database_exists = True

                response = yield from handler(request)
                return response
            return middleware
        return mysql_database_connector
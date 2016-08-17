#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from sqlalchemy.sql import func
import asyncio
import types
from aiopg.sa import create_engine
from sqlalchemy.schema import CreateTable
import sqlalchemy as sa
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime
import config
from sqlalchemy.orm import session
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy import Table

#---------------------------------------------------------------------------
#   `classic` style
#---------------------------------------------------------------------------
metadata = sa.MetaData()

#---------------------------------------------------------------------------
#   `classyc` style definition tables
#---------------------------------------------------------------------------
# куки сессий
cook  = sa.Table('blog_cook', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('cookie', sa.String(500)),
                 sa.Column('host', sa.String(200000)),
                 sa.Column('create', sa.DateTime(), default=func.now()),
                 sa.Column('dump_session', sa.String(20000000)),
                 sa.Column('status', sa.SmallInteger()),
                 sa.Column('lastconnect', sa.DateTime(),default=func.now()),
                 sa.Column('lastip', sa.String(1000)),
                 sa.Column('count_connection', sa.Integer()),
                 sa.Column('userid', sa.Integer()),
                 )
# пользователи
users = sa.Table('blog_user', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('cook_id', sa.Integer(), default=-1),
                 sa.Column('email', sa.String(length=200), unique=True),
                 sa.Column('creating', sa.DateTime(), default=func.now()),
                 sa.Column('password', sa.String(length=1000)),
                 sa.Column('role', sa.String(length=1000)),
                 )
# типы пользователей
role = sa.Table('blog_role', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String(200), unique=True),
                 )
# права пользователей по типу
roleperm = sa.Table('blog_roleperm', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('role_id', sa.ForeignKey('blog_role.id')),
                 sa.Column('read', sa.Boolean()),
                 sa.Column('write', sa.Boolean()),
                 sa.Column('edit', sa.Boolean()),
                 sa.Column('delete', sa.Boolean()),
                 )
# комментарии пользователей
comments= sa.Table('blog_comments', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('user_id', sa.ForeignKey('blog_user.id')),
                 sa.Column('data', sa.String(2000000)), # текст комментария
                 sa.Column('act', sa.Boolean()), # показывать на сайте
                 sa.Column('creating', sa.DateTime()), # время создания
                 )
# подписка на новые комментарии
commentsmail = sa.Table('blog_commentsmail', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('user_id', sa.ForeignKey('blog_user.id')),
                 )
# счетчик просмотров
counter = sa.Table('blog_counter', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('element_id', sa.Integer()), # идентификатор объекта tablename.id ->
                 sa.Column('count_view', sa.Integer()), # количество просмотров
                 )
# картинки в системе
image = sa.Table('blog_image', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String(5000)),  # идентификатор объекта tablename.id ->
                 sa.Column('path', sa.String(5000)),  # полный относительно static путь к файлу
                 sa.Column('alt', sa.String(5000)),  # количество просмотров
                 sa.Column('title', sa.String(5000)),  # количество просмотров
                 sa.Column('size', sa.Integer()),  # количество просмотров
                 sa.Column('creating', sa.DateTime(), default=func.now()),  # количество просмотров
                 )
# динамичные страницы
posts = sa.Table('blog_posts', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('title', sa.String(length=200)),  # title
                 sa.Column('author', sa.Integer()),  # --> user.id
                 sa.Column('data', sa.String(2000000)),  # body post
                 sa.Column('creating', sa.DateTime(), default=func.now()),  # количество просмотров
                 sa.Column('counter', sa.Integer(), default=0),  # количество просмотров
                 )
# теги
tags = sa.Table('blog_tags', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String(1000)),  # идентификатор объекта tablename.id ->
                 sa.Column('creating', sa.DateTime(), default=func.now()),
                 )
# теги связь постов с тэгами
tagslink = sa.Table('blog_tagslink', metadata,
                 sa.Column('post_id', sa.Integer, ),
                 sa.Column('tags_id', sa.Integer, ),
                 )
# категории
category = sa.Table('blog_category', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String(5000)),  # идентификатор объекта tablename.id ->
                 sa.Column('desc', sa.String(5000)),  # description
                 sa.Column('counter', sa.Integer(), default=0),  # количество публикаций
                 sa.Column('creating', sa.DateTime(), default=func.now()),  # количество просмотров
                 )
# теги связь постов с тэгами
catpost = sa.Table('blog_catpostlink', metadata,
                 sa.Column('post_id', sa.Integer, ),
                 sa.Column('cat_id', sa.Integer, ),
                 )


#---------------------------------------------------------------------------
#   list tables for exports
#---------------------------------------------------------------------------
list_tables = dict(
     cook = cook,
     users = users,
     role = role,
     perm = roleperm,
    comments = comments,
    commail = commentsmail,
    counter = counter,
    image = image,
    category = category,
    catpost = catpost,
    posts = posts,
    tags = tags,
    tagslink = tagslink,
)
#---------------------------------------------------------------------------
#   database utils
#---------------------------------------------------------------------------
class DatabaseUtils:
    def __init__(self,app):
        self.app = app
        self.db = self.app.database

    def runer(self,email, password,rolenameroot, roles, perms, tusers=None, trole=None, tperm=None):
        self.app.loop.run_until_complete(self.initdefaultvalues(roles=roles, perms=perms,trole=trole,tperm=tperm,
                                                                email=email,password=password,rolenameroot=rolenameroot, tusers=tusers))

    #---------------------------------------------------------------------------
    #   roleperm
    #---------------------------------------------------------------------------

#     # типы пользователей
# role = sa.Table('blog_role', metadata,
#                  sa.Column('id', sa.Integer, primary_key=True),
#                  sa.Column('name', sa.String(5000)),
#                  )
# # права пользователей по типу
# roleperm = sa.Table('blog_roleperm', metadata,
#                  sa.Column('id', sa.Integer, primary_key=True),
#                  sa.Column('role_id', sa.ForeignKey('blog_role.id')),
#                  sa.Column('read', sa.Boolean()),
#                  sa.Column('write', sa.Boolean()),
#                  sa.Column('edit', sa.Boolean()),
#                  sa.Column('delete', sa.Boolean()),
#                  )

    @asyncio.coroutine
    def check_exist(self, conn, trole, tperm, roles, perms):
        # role
        _rolcount_tmp = yield from conn.execute(trole.select())
        count_role = yield from _rolcount_tmp.fetchall()

        # perm
        _pc = yield from conn.execute(tperm.select())
        count_perm = yield from _pc.fetchall()

        if len(count_role) == len(roles) and len(count_perm) == len(count_role):
            return True
        else:
            return False

    @asyncio.coroutine
    def add_root_user(self, tusers, email, password, rolename):
        """добавление дефолтного рута"""
        with (yield from self.db) as conn:
            exist = yield from (yield from conn.execute(tusers.select().where(tusers.c.email == email))).fetchone()
            if exist:
                print("[INITROOT] already exist")
                return
            trans = yield from conn.begin()
            yield from conn.execute(tusers.insert().values(email=email, password=password, role=rolename))
            yield from trans.commit()
            return

    @asyncio.coroutine
    def initdefaultvalues(self, email, password,rolenameroot, roles, perms, tusers=None, trole=None, tperm=None):
        """дефолтная инициализация базы данных с дефолтными значениями"""
        yield from self.add_root_user(tusers=tusers, email=email, password=password, rolename=rolenameroot)
        yield from self.init_role(trole=trole,roles=roles, tperm=tperm,perms=perms)
        yield from self.init_perms(trole=trole, perms=perms, tperm=tperm)

    @asyncio.coroutine
    def init_perms(self, trole, perms, tperm):
        """создание новых правил доступа для дефолтьных ролей"""
        with (yield from self.db) as conn:
            trans = yield from conn.begin()

            # adding perm to each role
            res = yield from conn.execute(trole.select())
            roles = yield from res.fetchall()
            try:
                for _role in roles:
                    exist = yield from (yield from conn.execute(tperm.select().where(tperm.c.role_id==_role.id))).fetchone()
                    if not exist:
                        nowroles = perms.get(_role.name)
                        nowroles.update({'role_id':_role.id})
                        yield from conn.execute(tperm.insert().values(**nowroles))
                    else:
                        print("[INITPERMS] for role {} perms already exists".format(_role.name))
            except Exception as error:
                yield from trans.rollback()
                print("[INITPERMS]", error)
                return False

            yield from trans.commit()
            return

    @asyncio.coroutine
    def init_role(self, roles, trole, tperm, perms):
        """создание дефолтных ролей"""
        with (yield from self.db) as conn:
            trans = yield from conn.begin()
            try:
                for _role in roles:
                    q = trole.insert().values(name=_role)
                    yield from conn.execute(q)
            except Exception as error:
                yield from trans.rollback()
                print("[INITROLE]", error)
                return False

            yield from trans.commit()
            return

#---------------------------------------------------------------------------
#   declarative style definitions database models like
#---------------------------------------------------------------------------

# mapper `base` class for declarative style
# class Base(object):
#     @declared_attr
#     def __tablename__(cls):
#         """ table is name after class name"""
#         return cls.__name__.lower()
#
#     id = Column(Integer, primary_key=True)
#     """ adding automatic id all table creating new """
#
# # link class with map tables parents
# Base = declarative_base(cls=Base)

#---------------------------------------------------------------------------
#   models tables links with Base
#---------------------------------------------------------------------------
# class Users(Base):
#     __tablename__ = "blog_users"
#     cook_id = Column(Integer)
#     email = Column(String(50))
#     creating = Column(DateTime(), default=datetime.today())
#     password = Column(String(50))
#     role = Column(String(50), default=config.ANONYMOUS)
#
#
# class Cook(Base):
#     __tablename__ = "blog_cook"
#     cookie = Column(String(100))
#     host = Column(String(100))
#     creating = Column(DateTime(), default=datetime.today())
#     dump = Column(String)
#     status = Column(Boolean, default=False)
#     lastconnect = Column(DateTime(), default=datetime.today())
#     count_connections= Column(Integer, default = 0)
#     userid = Column(Integer, ForeignKey('blog_users.id'))


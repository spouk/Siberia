__author__ = 'spouk'
__all__ = ("Handlers",)
# ---------------------------------------------------------------------------
#   global imports
# ---------------------------------------------------------------------------
import asyncio
from datetime import datetime

from sqlalchemy import func, select, between

import forms
from Siberia.data import ProxyStack
from Siberia.decorators import decjin, decdbrock, autorize
from Siberia.ext.pagination import Pagination
from app import app
from forms import Login, Register, Restore

# ---------------------------------------------------------------------------
#   init decorators
# ---------------------------------------------------------------------------
newdjin = decjin(app=app, adding={})
decdbs = decdbrock(app=app)
auth = autorize(app=app, validate_list_roles=(app.c.role.root, app.c.role.admin))
pagi = Pagination(app=app, table=None, page=1, countonpage=app.c.config.pagination.count_on_page, db=app.database, namerouter=None)


# ---------------------------------------------------------------------------
#   views database support
# ---------------------------------------------------------------------------
class HandlersDatabaseSupport:
    def __init__(self, app):
        self.app = app

    @property
    def db(self):
        return self.app.database

    @asyncio.coroutine
    def cook_all(self, conn=None):
        dbs = self.db.cook
        result = yield from (yield from conn.execute(dbs.select())).fetchall()
        return result

    @asyncio.coroutine
    def user_get(self, id):
        """получить объект пользователя по id"""
        with (yield from self.db) as conn:
            u=self.db.users
            user = yield from(yield from conn.execute(u.select().where(u.c.id == id))).fetchone()
            return user


    @asyncio.coroutine
    def user_all(self, conn=None):
        dbs = self.db.users
        result = yield from (yield from conn.execute(dbs.select())).fetchall()
        return result

    @asyncio.coroutine
    def cook_get(self, cook, conn):
        """ получение записи по куку"""
        dbs = self.db.cook
        result = yield from (yield from conn.execute(dbs.select().where(dbs.c.cookie == cook))).fetchone()
        return result

    @asyncio.coroutine
    def user_email(self, email, conn):
        """ получение юзера по мылу"""
        dbs = self.db.users
        result = yield from (yield from conn.execute(dbs.select().where(dbs.c.email == email))).fetchone()
        return result

    @asyncio.coroutine
    def user_update(self, form, id):
        """обновление существующего пользователя"""
        with (yield from self.db) as conn:
            u = self.db.users
            r = self.db.role
            user = yield from(yield from conn.execute(u.select().where(u.c.id == id))).fetchone()
            # rol = yield from(yield from conn.execute(r.select().where(u.c.name == user.role)).fetchone())
            if user:
                q = dict(
                    password = form.password.data,
                    role = form.role.data
                )
                trans = yield from conn.begin()
                yield from conn.execute(u.update().values(**q))
                yield from trans.commit()
                return True
            return False

    @asyncio.coroutine
    def user_insert(self, form, conn=None, role=None):
        """регистрация нового юзверя """
        with (yield from self.db) as conn:
            user = yield from self.user_email(email=form.email.data, conn=conn)
            print("Form:", form)
            if user:
                form.email.errors.append("Пользователь с таким почтовым ящиком создан")
                return False

            trans = yield from conn.begin()
            dbs = self.db.users
            record = yield from self.cook_get(self.app.session.cook, conn=conn)
            q = dbs.insert().values(
                    cook_id=record and record.id or -1,
                    email=form.email.data,
                    password=form.password.data,
                    role=role or self.app.c.role.user,
                    creating=datetime.today(),
            )
            yield from conn.execute(q)
            yield from trans.commit()
            return True

    @asyncio.coroutine
    def login_validate(self, email, password):
        """ проверка данных формы на наличие в базе данных"""
        with (yield from self.db) as conn:
            dbs = self.db.users
            result = yield from (yield from conn.execute(dbs.select().where((dbs.c.email == email) & (dbs.c.password == password)))).fetchone()
            return result and result or None

    @asyncio.coroutine
    def login_update(self, userid):
        """обновляет сессию после авторизации"""
        with (yield from self.db) as conn:
            trans = yield from conn.begin()
            # обновление данных куке и сессии
            u = self.db.users
            c = self.db.cook

            savebox = yield from app.session.save()
            cook_obj = yield from (yield from conn.execute(c.select().where(c.c.cookie == app.session.cook))).fetchone()
            # вычистим старые кукисы связанные с этим пользователем
            # yield from conn.execute(c.delete().where(c.c.userid == userid))

            yield from conn.execute(u.update().values(cook_id=cook_obj.id))
            yield from conn.execute(c.update().values(userid=userid, dump_session=savebox))
            yield from trans.commit()

    @asyncio.coroutine
    def count_cookie(self):
        with (yield from self.db) as conn:
            c = self.db.cook
            u = self.db.users
            result = yield from(yield from conn.execute(select([func.count()]).select_from(c))).fetchone()
            print("RESULT:", result, result[0])
            # testing between
            rel = yield from (yield from conn.execute(select([u]).where(between(u.c.id, 12, 17)))).fetchall()
            print("Between: ", rel)
            #  testing limit/offset
            user = yield from(yield from conn.execute(u.select().limit(3).offset(3))).fetchall()
            print("Users:", user)

    @asyncio.coroutine
    def user_send_email(self, email, password):
        """формирование и отправка мыла на почту юзверю с паролем"""
        newmsg = self.app.c.config.login_restore
        newmsg._from = self.app.c.config.email
        newmsg._to = email
        newmsg._body = newmsg._body.format(password)
        yield from self.app.fn.send_email(**newmsg, debug=self.app.debuger)
        return True

    @asyncio.coroutine
    def login_restore(self, form):
        """проверка наличия почты в базе и обработка результата"""
        with (yield from self.db) as conn:
            u = self.db.users
            user = yield from self.user_email(form.email.data, conn)
            if not user:
                form.email.errors.append("Юзверя c таким мылом в системе не найдено")
                return False
            yield from self.user_send_email(email=form.email.data, password=user.password)
            return True

    @asyncio.coroutine
    def user_delete(self, ids):
        """удаление юзверей по id списку"""
        with (yield from self.db) as conn:
            trans = yield from conn.begin()
            u = self.db.users
            yield from conn.execute(u.delete().where(u.c.id.in_(ids)))
            yield from trans.commit()

    @asyncio.coroutine
    def role_get_choices(self):
        """получения списка ролей пользователей в системе"""
        with (yield from self.db) as conn:
            r = self.db.role
            roles = yield from (yield from conn.execute(r.select())).fetchall()
            return [(x.name, x.name) for x in roles]

    @asyncio.coroutine
    def roleperm_insert(self, conn, perms):
        p = self.db.perm
        q = p.insert().values(**perms)
        yield from conn.execute(q)

    @asyncio.coroutine
    def role_delete(self, ids):
        with (yield from self.db) as conn:
            r = self.db.role
            p = self.db.perm
            roles = yield from (yield from conn.execute(r.select().where(r.c.name.in_(ids)))).fetchall()
            trans = yield from conn.begin()
            for x in roles:
                yield from conn.execute(p.delete().where(p.c.role_id == x.id))
                yield from conn.execute(r.delete().where(r.c.id == x.id))
            yield from trans.commit()
            return

    @asyncio.coroutine
    def role_get(self, name):
        with (yield from self.db) as conn:
            r = self.db.role
            p = self.db.perm
            role = yield from (yield from conn.execute(r.select().where(r.c.name== name))).fetchone()
            perm = yield from (yield from conn.execute(p.select().where(p.c.role_id== role.id))).fetchone()

            return role, perm

    @asyncio.coroutine
    def role_update(self, form):
        """обновление существующей роли"""
        with (yield from self.db) as conn:
            r = self.db.role
            p = self.db.perm
            trans = yield from conn.begin()
            role = yield from (yield from conn.execute(r.select().where(r.c.name == form.rolename.data))).fetchone()

            perms = dict(
                    role_id=role.id,
                    write=form.write.data,
                    read=form.read.data,
                    edit=form.edit.data,
                    delete=form.delete.data,
            )
            yield from conn.execute(r.update().where(p.c.id == role.id).values(name=form.rolename.data))
            yield from conn.execute(p.update().where(p.c.role_id==role.id).values(**perms))
            yield from trans.commit()
            return True

    @asyncio.coroutine
    def role_insert(self, form):
        """создание новой роли в системе"""
        with (yield from self.db) as conn:
            r = self.db.role

            # check exist
            exist = yield from (yield from conn.execute(r.select().where(r.c.name == form.rolename.data))).fetchone()
            if exist:
                form.rolename.errors.append("Роль с таким именем уже существует в системе")
                return False

            trans = yield from conn.begin()

            # make newrole
            yield from conn.execute(r.insert().values(name=form.rolename.data))
            newrole = yield from(yield from conn.execute(r.select().where(r.c.name == form.rolename.data))).fetchone()

            # make new perms for newrole
            perms = dict(
                    role_id=newrole.id,
                    write=form.write.data,
                    read=form.read.data,
                    edit=form.edit.data,
                    delete=form.delete.data,
            )
            yield from self.roleperm_insert(conn, perms)
            yield from trans.commit()
            return True

    @asyncio.coroutine
    def online_stack(self):
        """получения списка текущих подключений по кукам"""
        with (yield from self.db) as conn:
            # variables
            c = self.db.cook
            u = self.db.users
            stack = self.app.fn.online
            cookies = yield from (yield from conn.execute(c.select().where(c.c.cookie.in_(list(stack.keys()))))).fetchall()
            # cook_ids = {x.userid:x for x in cookies}
            result_stack = []
            for cook in cookies:
                users = yield from (yield from conn.execute(u.select().where(u.c.cook_id == cook.id))).fetchall()
                result_stack.append((cook, users))

            return cookies
            # return result_stack


# ---------------------------------------------------------------------------
#   динамические рутеры + обработчики
# ---------------------------------------------------------------------------
class Handlers:
    def __init__(self, app):
        self.app = app
        self.db = HandlersDatabaseSupport(app=self.app)
        self.dbs = self.db.db

    @newdjin('tester.html')
    @asyncio.coroutine
    def tester(self, request):
        page = None
        # page = request.GET.get('page', None)
        print("Match page:", request.match_info['page'])
        print("Page", page, request.GET)
        return dict(spages=request.match_info['page'])

    # app.fn.get(r'/us/{name}/{page}', name="us", handler=handlers.us)
    @newdjin('us.html')
    async def us_get(self, request):
        pass

    # app.fn.get('/fuck',name='fucker', handler=handlers.fuck)
    @newdjin('news.html')
    @asyncio.coroutine
    def fuck(self, request):
        print("CALL `FUCK`", self.dbs, self.db, self.app.database)
        result = None
        with (yield from self.app.database) as conn:
            result = yield from self.db.cook_all(conn)
        return dict(fuck="fuck uoy", result=result)

    # app.fn.get('/', name="index", handler=handlers.index)
    @newdjin('index.html')
    async def index(self, request):
        print("INDEx-->", self.app, self.app.database)
        pass

    # app.fn.get('/debuginfo', name="debuginfo", handler=handlers.debuginfo)
    @newdjin('debuginfo.html')
    @asyncio.coroutine
    def debuginfo(self, request):
        print("Request path:", request.path)
        print("Request QS:", request.path_qs)
        print("Request GET:", request.GET)
        # current page
        page = request.GET.get('page', 1)
        yield from self.db.count_cookie()
        pagi = Pagination(app=self.app, table=self.db.db.users, page=page, countonpage=3, db=self.db.db, namerouter='debuginfo')
        yield from pagi.runer()
        pagelinks, records = pagi.result_func()
        return dict(pagelinks=pagelinks, records=records)

    # ---------------------------------------------------------------------------
    #   LOGIN /usr/login [get/post]
    # ---------------------------------------------------------------------------
    # app.fn.get('/user/login', name="login_get", handler=handlers.login)
    @newdjin('login.html')
    async def login(self, request):
        form = Login(app=self.app)
        return dict(form=form)

    # app.fn.post('/user/login', name="login_post", handler=handlers.login_post)
    # пост обработка вывод формы логина не требуется
    @newdjin('login.html')
    @asyncio.coroutine
    def login_post(self, request):
        formdata = yield from request.post()
        form = Login(formdata)
        if form.validate():
            user = yield from self.db.login_validate(email=form.email.data, password=form.password.data)
            if user is None:
                form.email.errors.append("Такого пользователя в системе нет")
                return dict(form=form)
            else:
                app.session.update(dict(
                        user=ProxyStack(userid=user.id, cookid=user.cook_id, email=user.email,
                                        created=user.creating, password=user.password, role=user.role,
                                        online=True),
                ))
                yield from self.db.login_update(userid=user.id)
                # вернем назад по реферу если рефер есть
                ref = app.session.get('ref', None)
                if ref:
                    return app.fn.redirect(**ref.rdy)
        # если нет рефа то пулим на главную
        return app.fn.redirect('index')

    # app.fn.get('/user/unlogin', name="unlogin", handler=handlers.unlogin)
    @newdjin('logout.html')
    async def logout(self, request):
        if app.session.get('user', None) is None:
            return app.fn.redirect('not found fucken bitch')
        app.session.user.online = False
        return app.fn.redirect('index')

    # ---------------------------------------------------------------------------
    #   REGISTER /usr/register [get/post]
    # ---------------------------------------------------------------------------

    # app.fn.get('/user/register', name="register_get", handler=handlers.register_get)
    @newdjin('login.html')
    async def register_get(self, request):
        form = Register()
        return dict(form=form)

    # app.fn.post('/user/register', name="register_post", handler=handlers.register_post)
    @newdjin('login.html')
    @asyncio.coroutine
    def register_post(self, request):
        formdata = yield from request.post()
        form = Register(formdata)
        if not form.validate():
            return dict(form=form)
        result = yield from self.db.user_insert(form=form)
        return dict(result=result, form=form)

    # ---------------------------------------------------------------------------
    #   RESTORE /usr/restore [get/post]
    # ---------------------------------------------------------------------------

    # app.fn.get('/user/restore', name="restore_get", handler=handlers.restore_get)
    @newdjin('login.html')
    @asyncio.coroutine
    def restore_get(self, request):
        form = Restore(app=self.app)
        return dict(form=form)

    # app.fn.post('/user/restore', name="restore_post", handler=handlers.restore_post)
    @newdjin('login.html')
    @asyncio.coroutine
    def restore_post(self, request):
        result = None
        formdata = yield from request.post()
        form = Restore(formdata)
        if form.validate():
            result = yield from self.db.login_restore(form)
        return dict(result=result, form=form)

    # ---------------------------------------------------------------------------
    #   adminka
    # ---------------------------------------------------------------------------
    #
    @auth
    @newdjin('adminka/adminindex.html')
    async def adminka_root(self, request, answer):
        pass

    # ---------------------------------------------------------------------------
    #   adminka/users
    # ---------------------------------------------------------------------------

    # app.fn.get(realadm.format(adm, r'/users'), name="admin_users", handler=handlers.adminka_root)
    # app.fn.get(realadm.format(adm, r'/users/p={p:\d+}'), name="admin_users_page", handler=handlers.adminka_users)
    @auth
    @newdjin('adminka/admin_users.html')
    @asyncio.coroutine
    def adminka_users(self, request, answer):
        answer.pagelinks = None
        answer.records = None
        answer.page = self.app.fn.getarg('p') or 1
        if answer.page:
            pagi.init(table=self.db.db.users, page=answer.page, namerouter='admin_users_page')
            yield from pagi.runer()
            answer.pagelinks, answer.records = pagi.result_func()
        return dict(answer=answer)

    @auth
    @newdjin('adminka/admin_users.html')
    @asyncio.coroutine
    def adminka_users_fn(self, request, answer):
        print("--> METHOD:", request.method)
        answer.form = forms.UserCreate()
        answer.fn = self.app.fn.getarg('fn')
        answer.id = self.app.fn.getarg('id')

        if request.method == "GET" and  answer.fn in ('delete',):
            return app.fn.redirect('admin_users')

        answer.form.role.choices = yield from self.db.role_get_choices()
        if answer.id:
            user = yield from self.db.user_get(id=answer.id)
            answer.form.email.data = user.email
            answer.form.password.data = user.password
            answer.form.role.data = user.role

        if request.method == 'POST':
            post = yield from request.post()
            if answer.fn in ('create', 'update'):
                answer.form = forms.UserCreate(post)
                answer.form.role.choices = yield from self.db.role_get_choices()

            if answer.fn == "delete":
                if 'ids' in post:
                    answer.ids = post.getall('ids')
                    if answer.ids:
                        yield from self.db.user_delete(ids=answer.ids)
                        app.flasher.send('adminka', 'success', "Пользователи {!s} успешно удалены".format(answer.ids))
                    else:
                        app.flasher.send('adminka', 'info', "Чтобы что-то удалить, надо это `что-то` выделить сперва")
                else:
                    app.flasher.send('adminka', 'info', "Чтобы что-то удалить, надо это `что-то` выделить сперва")

                return app.fn.redirect('admin_users_page', parts={'p':1})

            if answer.fn == "create":
                answer.form = forms.UserCreate(post)
                answer.form.role.choices = yield from self.db.role_get_choices()
                if answer.form.validate():
                    result = yield from self.db.user_insert(form=answer.form, role=answer.form.role.data)
                    if result:
                        app.flasher.send('adminka', 'success', "Пользователь {} успешно создан".format(answer.form.email.data))
                        return app.fn.redirect('admin_users')
                else:
                    app.flasher.send('adminka', 'info', "В форме обнаружены ошибки , исправьте и попробуйте снова")

            if answer.fn == "update":
                if answer.form.validate():
                    result = yield from self.db.user_update(form=answer.form, id=answer.id)
                    if result:
                        app.flasher.send('adminka', 'info', "Сведения о пользователе {!s} успешно изменены".format(answer.form.email.data))
                        return app.fn.redirect('admin_users')
                    else:
                        app.flasher.send("adminka", "error", "[user_update]--не найден в базе данных пользователь с id: {!s}".format(id))
                else:
                    app.flasher.send('adminka', 'info', "В форме обнаружены ошибки , исправьте и попробуйте снова")


        # render answer
        return dict(answer=answer)

    # ---------------------------------------------------------------------------
    #   adminka/online
    # ---------------------------------------------------------------------------

    @auth
    @newdjin('adminka/admin_online.html')
    @asyncio.coroutine
    def adminka_online(self, request, answer):
        answer.pagelinks = None
        answer.records = None

        if request.method == "GET":
            answer.page = self.app.fn.getarg('p') or 1
            print("Answer Page:", answer)
            if answer.page:
                online = yield from self.db.online_stack()
                print("Online func:", len(online), online)
                pagi.init(random_obj=online, page=answer.page, namerouter='admin_online_page')
                yield from pagi.runer()
                answer.pagelinks, answer.records = pagi.result_func()

        return dict(answer=answer)

    # ---------------------------------------------------------------------------
    #   adminka/roles
    # ---------------------------------------------------------------------------
    @auth
    @newdjin('adminka/admin_roles.html')
    @asyncio.coroutine
    def adminka_roles(self, request, answer):
        answer.get = request.GET
        answer.roles = yield from self.db.role_get_choices()
        return dict(answer=answer)

    @auth
    @newdjin('adminka/admin_roles.html')
    @asyncio.coroutine
    def adminka_roles_fn(self, request, answer):
        answer.fn = self.app.fn.getarg('fn')
        answer.id = self.app.fn.getarg('id')
        if answer.id:
            role,perm  = yield from self.db.role_get(answer.id)
            print("Role:", role, role.id, role.name, perm)
            answer.form = forms.RoleCreate(obj=role)
            answer.form.rolename.data = role.name
            answer.form.write.data = perm.write
            answer.form.read.data = perm.read
            answer.form.edit.data = perm.edit
            answer.form.delete.data = perm.delete
        else:
            answer.form = forms.RoleCreate()

        if request.method == 'POST':
            post = yield from request.post()
            answer.form = answer.fn in ('create', 'update') and forms.RoleCreate(post)

            if answer.fn == "delete":
                if 'ids' in post:
                    answer.ids = post.getall('ids')
                    yield from self.db.role_delete(answer.ids)
                    app.flasher.send('adminka', 'success', "Роли {!s} успешно удалены".format(answer.ids))
                else:
                    app.flasher.send('adminka', 'info', "Чтобы что-то удалить, надо это `что-то` выделить сперва")
                return app.fn.redirect('admin_roles')

            if answer.fn == "create":
                if answer.form.validate():
                    result = yield from self.db.role_insert(form=answer.form)
                    if result:
                        app.flasher.send('adminka', 'success', "Роль {!s} успешно создана".format(answer.form.rolename.data))
                        return app.fn.redirect('admin_roles')
                else:
                    app.flasher.send('adminka', 'info', "В форме обнаружены ошибки , исправьте и попробуйте снова")

            if answer.fn == "update":
                if answer.form.validate():
                    result = yield from self.db.role_update(form=answer.form)
                    if result:
                        app.flasher.send('adminka', 'info', "Record {!s} success change".format(answer.form.rolename.data))
                        return app.fn.redirect('admin_roles')
                else:
                    app.flasher.send('adminka', 'info', "В форме обнаружены ошибки , исправьте и попробуйте снова")

        # render answer
        return dict(answer=answer)


    # ---------------------------------------------------------------------------
    #   adminka/category
    # ---------------------------------------------------------------------------

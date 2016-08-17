__author__ = 'spouk'
#---------------------------------------------------------------------------
#   базовый импорт
#---------------------------------------------------------------------------
from handlers import app,Handlers
#---------------------------------------------------------------------------
#   настройка
#---------------------------------------------------------------------------
handlers = Handlers(app=app)
# ---------------------------------------------------------------------------
#   фиксированные рутеры
# ---------------------------------------------------------------------------
app.router.add_static(prefix='/static/css', path='static/css', name='css')
app.router.add_static(prefix='/static/font', path='static/font', name='font')
app.router.add_static(prefix='/static/img', path='static/img', name='img')
app.router.add_static(prefix='/static/js', path='static/js', name='js')
#---------------------------------------------------------------------------
#   изменяющиеся рутеры
#---------------------------------------------------------------------------
app.fn.get('/', name="index", handler=handlers.index)
app.fn.get('/fuck',name='fucker', handler=handlers.fuck)
app.fn.get('/debuginfo', name="debuginfo", handler=handlers.debuginfo)
app.fn.get('/user/login', name="login_get", handler=handlers.login)
app.fn.post('/user/login', name="login_post", handler=handlers.login_post)
app.fn.get('/user/restore', name="restore_get", handler=handlers.restore_get)
app.fn.post('/user/restore', name="restore_post", handler=handlers.restore_post)
app.fn.get('/user/register', name="register_get", handler=handlers.register_get)
app.fn.post('/user/register', name="register_post", handler=handlers.register_post)
app.fn.get('/user/logout', name="logout", handler=handlers.logout)

# adminka routes
adm = app.c.config.adminka.routepath
realadm = r"{}{}"

app.fn.get(adm, name="adminka", handler=handlers.adminka_root)
# users
app.fn.get(realadm.format(adm, r'/users'), name="admin_users", handler=handlers.adminka_users)
app.fn.get(realadm.format(adm, r'/users/{p:\d+}'), name="admin_users_page", handler=handlers.adminka_users)
app.fn.route(realadm.format(adm, r'/users/{fn}'), name="admin_users_fn", handler=handlers.adminka_users_fn)
app.fn.route(realadm.format(adm, r'/users/{fn}/{id:\d+}'), name="admin_users_fn_id", handler=handlers.adminka_users_fn)

# online
app.fn.get(realadm.format(adm, r'/online'), name="admin_online", handler=handlers.adminka_online)
app.fn.get(realadm.format(adm, r'/online/{p:\d+}'), name="admin_online_page", handler=handlers.adminka_online)

# roles
app.fn.get(realadm.format(adm, r'/roles'), name="admin_roles", handler=handlers.adminka_roles)
app.fn.route(realadm.format(adm, r'/roles/{fn}'), name="admin_roles_fn", handler=handlers.adminka_roles_fn)
app.fn.route(realadm.format(adm, r'/roles/{fn}/{id:[a-z]\w+}'), name="admin_roles_fn_id", handler=handlers.adminka_roles_fn)

# app.fn.route(realadm.format(adm, r'/roles[\S]'), name="admin_roles", handler=handlers.adminka_roles)

# app.fn.get(r'/c/{arg}={action}', name="ac", handler=handlers.suck)
# arg = fn,p
# action = fn:create, fn:update, p:1..9

app.fn.get(r'/tester/{page:\d+}', name="tester", handler=handlers.tester)
app.fn.get(r'/tester/page={page:\d+}', name="tester_page", handler=handlers.tester)


# app.fn.get(r'/tester/{page:\d+}', name="tester", handler=handlers.tester)

# testing make routes variables
app.fn.get(r'/us/{name}/{page}', name="us", handler=handlers.us_get)

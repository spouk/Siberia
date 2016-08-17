#!/usr/local/bin/python
__author__ = 'spouk'

from Siberia.plug.plugin_jinja import JinjaPlugin
from Siberia.plug.plugin_mysql import MysqlPlugin
from Siberia.plug.plugin_session import SessionPlugin
from models import metadata, list_tables, cook, users, DatabaseUtils, role, roleperm
from app import app


# assign plugins
app.fn.install_plugin(JinjaPlugin(app=app))
app.fn.install_plugin(MysqlPlugin(app=app, **app.c.database, metadata=metadata))
app.fn.install_plugin(SessionPlugin(app, user_table=users, cook_table=cook))

# импорт рутеров, надо импортить после подключение базы данных ( плагина )
import views

app.fn.maproute()
app.fn.before_run_stack()

dbinit = DatabaseUtils(app=app)
dbinit.runer(email=app.c.config.defaultroot.mail,password=app.c.config.defaultroot.password,rolenameroot=app.c.config.defaultroot.role,tusers=users,\
             roles=app.c.role.values(), perms=app.c.perm,trole=role,tperm=roleperm)

print("App flasher:", app.flasher)
app.flasher.send(g='Fucker',t='newtype',m='Simplemessage')
app.flasher.send(g='Fucker',t='newtype2',m='Simplemessage2')
app.flasher.send('Fucker','newtype3','Simplemessage3')
app.flasher.send('Fucker2','newtype','Simplemessage3')

t = 'newtype'
g = 'Fucker'

print("All type: [{}]".format(t), app.flasher.get_t(t))
print("All group: [{!s}]".format(g), app.flasher.get_g(g))
print("App flasher:", app.flasher._stack, app.flasher._counter)
print("Flasher popper:", app.flasher.get())
print("App flasher:", app.flasher._stack, app.flasher._counter)
print("Flasher popper:", app.flasher.get())
print("App flasher:", app.flasher._stack, app.flasher._counter)
print("Flasher popper:", app.flasher.get())
print("App flasher:", app.flasher._stack, app.flasher._counter)

app.run()


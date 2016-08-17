#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from .exceptions import SiberiaPluginException
from .loggers import metawrapper
from .data import ProxyStack

#---------------------------------------------------------------------------
#   plugin meta
#---------------------------------------------------------------------------
class SiberiaMeta(type):
    """ plugin metaclass """

    def __new__(cls, name, parent, attr):

        REQ = ('version','api','name', 'middleware')

        assert 'plugin_stack' in attr, "Ошибка структуры плагина, нехватка нужной структуры"

        # проверка наличия нужных методов
        if "setup" not in attr:
            raise SiberiaPluginException("Plugin `{}` must have  release method `setup` ".format(name))

        # проверка наличия нужной структуры плагина
        if not (len([True for x in REQ if x in attr['plugin_stack'] or False]) == len(REQ)) :
            raise SiberiaPluginException("Plugin `{}` must have  attributes `api` `name` `version` ".format(name))

        # обертка логгирования
        metawrapper(attr)

        return super(SiberiaMeta, cls).__new__(cls, name, parent, attr)

#---------------------------------------------------------------------------
#   plugin inteface
#---------------------------------------------------------------------------

class SiberiaPlugin(metaclass=SiberiaMeta):
    """ plugin interface"""
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "Session",
        version = 0.1,
        middleware = True,
    )

    def setup(self):
        raise NotImplementedError

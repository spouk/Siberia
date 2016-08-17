#!/usr/local/bin/python
__author__ = 'spouk'

__all__ = 'ProxyStack'

#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from . exceptions import SiberiaDataWrong
from . loggers import MetaLogger
#---------------------------------------------------------------------------
#   data structures
#---------------------------------------------------------------------------
class ProxyStack(dict, metaclass=MetaLogger):
    # def __init__(self, size=None):
    #     self.size = size

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        # if self.size and len(self.items()) >= self.size:
        #     print('[PROXYSTACK] размер стака составляет {} вы пытаетесть добавить в стак еще один элемент. Ошибка.'.format(self.size))
        # else:
            self[key] = value

    def __delattr__(self, item):
        del self[item.lower()]





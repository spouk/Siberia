#!/usr/local/bin/python
__author__ = 'spouk'
__all__=  ("MetaLogger",)
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
import logging
import logging.config
import inspect
import functools
import os

#---------------------------------------------------------------------------
#   config loggin
#---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#   base loggers config // can ovveride in config.files project or
#   update `app.config.loggers` = you dict configuration
#   warning: default config enable only stream log
#   other u need config u project
# ---------------------------------------------------------------------------
LOG_FORMAT  = '%(asctime)s [m] %(module)-25s < [fn] %(funcName)-25s > [ Line : %(lineno)-4d] %(levelname)-10s %(message)s'

LOG_DICT_DEFAULT = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default_format',
        },
    },
    'formatters': {
        'default_format': {
            'format': LOG_FORMAT,
        },
        'email': {
            'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n'
                      'Line: %(lineno)d\nMessage: %(message)s',
        },
    },
    'loggers': {
        '': {
            'propagate': True,
            'level': 'INFO',
            'handlers': ['console']
        },
    }
}
# load base config
logging.config.dictConfig(LOG_DICT_DEFAULT)
# get logger
log = logging.getLogger(__name__)
# set default log level
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------
#   logger decorators
#---------------------------------------------------------------------------
variants = (inspect.isawaitable, inspect.iscoroutine, inspect.iscoroutinefunction)
iscoro = lambda fn: any((check(fn) for check in variants))

def function_logger_async(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        result = None
        try:
            result = await fn(*args, **kwargs)
        except Exception as error:
            log.debug("[-LOGGER-] [ async : {} ] {} `{}` {!s}".format(True, fn.__name__, error, fn))
        return result
    return wrapper

def function_logger_sync(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = fn(*args, **kwargs)
        except Exception as error:
            log.debug("[-LOGGER-] [ async : {} ] {} `{}`".format(False, fn.__name__, error))
        return result
    return wrapper

func_decor=lambda fn: iscoro(fn) and function_logger_async(fn) or function_logger_sync(fn)

def metawrapper(attrs):
        # filter callable not builtins methods
        accept_fn = {k:v for k,v in attrs.items() if not k.startswith('__') and callable(v)}
        # wrappers filtered callable methods swtich async/sync style
        updater_decor = {k : func_decor(v) for k,v in accept_fn.items()}
        # update attrs dict
        attrs.update(updater_decor)

#---------------------------------------------------------------------------
#   meta class
#---------------------------------------------------------------------------
class MetaLogger(type):
    def __new__(cls, name, parent, attrs):
        log.info("[META_LOGGER CALL] {} {}".format(name, attrs))
        # inject logger decorator
        metawrapper(attrs)
        # inject log
        attrs['log'] = log
        # make class
        return type.__new__(cls, name, parent, attrs)




#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
import inspect

#---------------------------------------------------------------------------
#   applications exceptions // base class
#---------------------------------------------------------------------------
class SiberiaException(Exception):
    """ global application exceptions """
    pass

#---------------------------------------------------------------------------
#   exception parts
#---------------------------------------------------------------------------

class SiberiaDataWrong(SiberiaException):

    # defaults
    _msg = "Wrong data type"
    _data = "`type data undefined`"
    def __init__(self,exc, msg=None, data=None):
        self.exc = exc
        self.msg = msg
        self.data = data


class SiberiaPluginException(SiberiaException):

    def __init__(self,exc=None, msg=None):
        self.exc = exc
        self.msg = msg

class SiberiaPluginInvalidType(SiberiaException):
    pass

class SiberiaPluginInvalidConfig(SiberiaException):
    pass



class SiberiaMiddlewareWrongType(SiberiaException):
    pass


class SiberiaHTTPRouteErrors(SiberiaException):
    pass




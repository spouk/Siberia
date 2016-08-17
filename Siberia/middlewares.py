#!/usr/local/bin/python
__author__ = 'spouk'
__all__ =['CatcherPlugin']

#---------------------------------------------------------------------------
#   global import
#---------------------------------------------------------------------------
from . data import ProxyStack
from . plugins import SiberiaPlugin
from aiohttp.web import  HTTPError
#---------------------------------------------------------------------------
#   moddlewares
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#   additions int middlwares for `Siberia` (not for developing)
#---------------------------------------------------------------------------
class CatcherPlugin(SiberiaPlugin):

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "catcher",
        version = 0.1,
        middleware = True,
    )

    # config for session
    config = ProxyStack()

    def __init__(self, app):
        self.app = app

    def setup(self):
        # adding middle to application
        self.app.middlewares.append(self.catcher(app=self.app))

    def catcher(self, app):
        """ middleware catcher """
        async def _catcher(app, handler):
            async def middleware(request):
                result = await app.router.resolve(request)
                if hasattr(self.app, 'log') and self.app.log and self.app.c.debuger:
                    self.app.log.info("[CATCHER_PLUGIN] -  Method: {} -  Path: {} - Cookies: {} - Route request[resolve]: "
                        "{}".format(request.method, request.path,request.cookies, result._route))

                # return await handler(request)
                try:
                    return await handler(request)
                except HTTPError as er:
                    if str(er.status_code) in self.app.c.errors:
                        return await app.render(self.app.c.errors[str(er.status_code)])
                    return er

            return middleware
        return _catcher



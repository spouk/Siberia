#!/usr/local/bin/python
__author__ = 'spouk'
__all__ = ('JinjaPlugin',)
__version__ = 0.1
__name__ = 'Jinja2Plugin for Siberia'
__middleware__ = True
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader, TemplateError
from ..plugins import SiberiaPlugin
from ..data import ProxyStack
from aiohttp import web, request

#---------------------------------------------------------------------------
#   implement jinja2 plugin for Siberia
#---------------------------------------------------------------------------
class JinjaPlugin(SiberiaPlugin):

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "Jinja2",
        version = 0.1,
        middleware = False,
    )

    # config for session
    config = ProxyStack(
        filters = ProxyStack(),
        globals = ProxyStack(),
        template_path = ['templates/'],
        env_config = ProxyStack(
            trim_blocks=True,
            lstrip_blocks=True,
        ),
        inject_template = ProxyStack(),
    )

    def __init__(self, app, template_path=None):
        self.app = app
        self.addtemplate(template_path)

    def addtemplate(self, template):
        if template:
            self.config.template_path.append(template)
        self.initjinja()
        return

    def initjinja(self):
        # check app config
        if hasattr(self.app.c.config,'jinja_filters'):
            self.config.filters.update(self.app.c.config.jinja_filters)
        if hasattr(self.app.c.config,'jinja_globals'):
            self.config.globals.update(self.app.c.config.jinja_globals)

        print("Jinja filters and globals:", self.config)

        self.config.template_path = self.config.template_path
        self.jinja2env = Environment(loader=FileSystemLoader(self.config.template_path), **self.config.env_config)
        self.jinja2env.filters.update(self.config.filters)
        self.jinja2env.globals.update(self.config.globals)
        return

    def setup(self):
        # inject plugin to app, replace default self.render to jinja2
        self.app.render = self.jrender

    async def jrender(self, page, request=None, _string=False, **kwargs):
        __doc__  = "async render template jinja template"

        kwargs.update(**self.config.inject_template)
        kwargs.update({'app': self.app})
        kwargs.update({'request': request})
        kwargs.update({'url_for': self.app.fn.url_for})
        # `None` for simulate error if found in template or `page` input data
        result = None
        try:
            if isinstance(page, str) and _string:
                result = self.jinja2env.from_string(page).render(**kwargs)
                return result
            result = self.jinja2env.get_template(page).render(**kwargs)
        except Exception as error:
            if self.app.log:
                self.app.log.error(error)
        finally:
            result = result.encode()
        return web.Response(body=result)



#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'
#---------------------------------------------------------------------------
#   global imports
#---------------------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader, TemplateError
from ..plugins import SiberiaPlugin
from ..data import ProxyStack
from aiohttp import web, request
from hashlib import md5
import uuid
import random
import bs4


from wtforms.csrf.core import CSRF
#---------------------------------------------------------------------------
#  integrating wtforms
#---------------------------------------------------------------------------
class FormsCSRF(CSRF):
    """
    Generate a CSRF token based on the user's IP. I am probably not very
    secure, so don't use me.
    """
    def __init__(self, app):
        self.app = app

    def setup_form(self, form):
        return super(FormsCSRF, self).setup_form(form)

    def generate_csrf_token(self, csrf_token):
        token = None
        if self.app and hasattr(self.app, 'csrf'):
            token = self.app.csrf.csrf_token
        else:
            print("INSTALL CSRFPLUGIN for CSRF FORM")
        print("CSRF_TOKEN FROM FormsCSRF", csrf_token)
        return token

    def validate_csrf_token(self, form, field):
        if field.data != field.current_token:
            raise ValueError('Invalid CSRF')



#---------------------------------------------------------------------------
#   CSRF integrated with WTForms
#---------------------------------------------------------------------------
class CSRFPlugin(SiberiaPlugin):

    # plugin definitions variables
    plugin_stack = ProxyStack(
        api = 0.1,
        name = "CSRFPlugin",
        version = 0.1,
        middleware = True,
    )
    # config for session
    config = ProxyStack(

    )
    def __init__(self, app, csrf_salt=None, parser="html.parser"):

        self.app = app
        self.csrf_salt = csrf_salt or random.gammavariate(1,100)
        self.csrf_token = None
        self.csrf_token_last = None
        self.csrf_html = self._csrf_html
        self.csrf_meta = None
        self.csrf_meta_html = self._csrf_meta_html
        self.parser = parser

        self.POST = False

        self.formsCSRF = FormsCSRF(app=self.app)

    def setup(self):

        # adding middle to application
        if hasattr(self.app, 'middlewares'):
            self.app.middlewares.append(self.csrfplugin(app=self.app))

        # inject plugin application
        self.app.csrf = self

    def _csrf_meta_html(self):
        """html widget for hidden csrf_token meta"""
        return "<meta name='csrf_token' content='{}' >".format(self.csrf_token)

    def _csrf_html(self):
        """html widget for hidden csrf_token"""
        return "<input type='hidden' name='csrf_token' value='{}' >".format(self.csrf_token)

    async def _generate_csrf_token(self):
        stroka  = str(uuid.uuid4()) + str(self.csrf_salt)
        result =md5(stroka.encode()).hexdigest()
        return result

    async def parse_meta_csrf(self, request):
        """[async] parse request `csrf` from meta"""
        # parse `META` token
        text = await request.text()
        text_raw = await request.read()
        print(text, text_raw)
        pars_result = bs4.BeautifulSoup(text, self.parser).findAll('meta')
        found = filter(lambda x: x.get('name',None) and x.get('name') == 'csrf_token', pars_result)

        # update variable
        self.csrf_meta = found and found[0].get('content', None) or None
        return

    def csrfplugin(self, app):
        """ middleware csrfplugin"""
        async def _csrfplugin(app, handler):
            async def middleware(request):
                # csrfplugin
                if self.csrf_token is None:
                    self.csrf_token = await self._generate_csrf_token()

                if request.method == "POST":
                    self.POST=True
                    self.csrf_token_last = self.csrf_token
                    # print("[FOUND POST REQUEST]\nCSRF_TOKEN: {}\nLAST_TOKEN: {}".format(self.csrf_token, self.csrf_token_last))
                    # await self.parse_meta_csrf(request=request)
                    # print('Make new token ')
                    self.csrf_token = await self._generate_csrf_token()
                    # print("New token: {} {}".format(self.csrf_token, self.csrf_token_last))

                if request.method == "GET":
                    self.POST=False
                    # generate new token
                    # self.csrf_token_last = self.csrf_token or None
                    # self.csrf_token = await self._generate_csrf_token()

                # print("Body", request.body)
                # if debug on log
                if hasattr(self.app, 'log') and self.app.log and self.app.debuger:
                    self.app.log.info("[CSRF_PLUGIN] [CSRF_TOKEN: {}] [OLD_TOKEN: {}] [META_TOKEN: {}]".format(self.csrf_token,self.csrf_token_last, self.csrf_meta))
                response = await handler(request)
                return response
            return middleware
        return _csrfplugin








#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from wtforms import *
from wtforms.widgets.html5 import EmailInput
from wtforms.widgets.core import CheckboxInput, SubmitInput
from wtforms.csrf.core import CSRF
from wtforms.validators import DataRequired
from hashlib import md5
import uuid
import random
import datetime

SECRET_KEY = 'somesecret'



class FormsCSRF(CSRF):
    """
    Generate a CSRF token based on the user's IP. I am probably not very
    secure, so don't use me.
    """
    def setup_form(self, form):
        return super(FormsCSRF, self).setup_form(form)

    def generate_csrf_token(self, csrf_token):
        token = md5( (str(SECRET_KEY) + datetime.date.today().strftime("%Y/%m/%d")).encode()).hexdigest()
        print("CSRF_TOKEN FROM FormsCSRF: {}".format(token))
        return token

    def validate_csrf_token(self, form, field):
        print("====VALIDATE process===")
        # print("VALIDATE METHOD current_token:", field.current_token)
        # print("VALIDATE METHOD form_data:", type(field.data), field, field.data)
        # print("VALIDATE form: ", form.__dict__)
        # for k,v in form.__dict__.items():
        #     print("{:<30}{!s:<30}".format(k,v))
        # print(form.username.data)
        # print(form.password.data)
        # print(form.csrf_token.data)
        if field.data != field.current_token:
            raise ValueError('Invalid CSRF')


class MyBaseForm(Form):
    class Meta:
        csrf = True  # Enable CSRF
        csrf_class = FormsCSRF # Set the CSRF implementation
        # csrf_secret = b'foobar'  # Some implementations need a secret key.
        # Any other CSRF settings here.
    submit = SubmitField("Отправить форму")

class Login(MyBaseForm):
    email = StringField('Email')
    password = PasswordField('Password')

class Register(MyBaseForm):
    username = StringField('Username', validators=[DataRequired("Имя пользователя нужно указать")])
    password = PasswordField('Password', validators=[DataRequired("Пароль пустой, надо добавить")])
    email = StringField("Email",validators=[DataRequired("Почтовый ящик укажи")])
    save_session = BooleanField("Save session? ")


class Restore(MyBaseForm):
    email = StringField("Email", validators=[DataRequired("Почтовый ящик укажи")] )


class UserCreate(MyBaseForm):
    email = StringField("Email", validators=[DataRequired("Почтовый ящик укажи")] )
    password = PasswordField('Password', validators=[DataRequired("Пароль пустой, надо добавить")])
    role = SelectField('Role', coerce=str)

class RoleCreate(MyBaseForm):
    rolename = StringField("Имя новой роли", validators=[DataRequired("Поле не может быть пустым")])
    write = BooleanField("Запись")
    read = BooleanField("Чтение", validators=[DataRequired("Поле не может быть пустым")])
    edit = BooleanField("Правка")
    delete = BooleanField("Удаление")





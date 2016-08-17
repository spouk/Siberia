#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from config import config
from models import list_tables
from Siberia.application import Application

app = Application(config=config, debug=True, debuger=True, list_tables=list_tables)






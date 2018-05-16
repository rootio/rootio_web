# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.cache import Cache
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.restless import APIManager
from flask.ext.wtf.csrf import CsrfProtect
import zmq

db = SQLAlchemy()

mail = Mail()

cache = Cache()

login_manager = LoginManager()

oid = OpenID()

rest = APIManager()

csrf = CsrfProtect()

zmq_context = zmq.Context()

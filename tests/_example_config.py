# -*- coding: utf-8 -*-

import os
from utils import make_dir

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_FOLDER_PATH = os.path.join(PROJECT_ROOT, 'instance')

class BaseConfig(object):
    PROJECT = "rootio"
    SECRET_KEY = 'some random key'
    CONTENT_DIR = "/var/content"
    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
    ZMQ_BIND_ADDR = "tcp://127.0.0.1:55777"
    ZMQ_SOCKET_TYPE = "PUB"
    ACCEPT_LANGUAGES = {'en':'English'}

class DefaultConfig(BaseConfig):
    pass

class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://' # store db in memory

    MAIL_DEFAULT_SENDER = 'test@example.com'

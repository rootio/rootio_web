# -*- coding: utf-8 -*-

import os

from flask import Flask, g, request, render_template, session
from flask.ext.babel import Babel

from flask.ext.admin import Admin

from .config import DefaultConfig
from .admin import admin_routes, AdminHomeView
from .user import User, user
from .settings import settings
from .frontend import frontend
from .api import api, restless_routes
from .rootio import rootio
from .radio import radio
from .onair import onair
from .telephony import telephony
from .messenger import messenger
from .content import content

from .extensions import db, mail, cache, login_manager, oid, rest, csrf, zmq_context
from .utils import CustomJSONEncoder, read_config

import zmq

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    frontend,
    user,
    rootio,
    radio,
    onair,
    telephony,
    settings,
    api,
    messenger,
    content,
)


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_relative_config=True)
    app.json_encoder = CustomJSONEncoder

    configure_app(app, config)
    configure_hook(app)
    configure_logging(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_messenger(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    app.logger.info('application started')

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('rootio.cfg')

    if config:
        app.config.from_object(config)

    # Use instance folder instead of env variables to make deployment easier.
    #app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-mail
    mail.init_app(app)

    # flask-cache
    cache.init_app(app)

    # flask-babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        #TODO, first check user config?
        g.accept_languages = app.config.get('ACCEPT_LANGUAGES')
        accept_languages = g.accept_languages.keys()
        browser_default = request.accept_languages.best_match(accept_languages)
        if 'language' in session:
            language = session['language']
            #current_app.logger.debug('lang from session: %s' % language)
            if not language in accept_languages:
                #clear it
                #current_app.logger.debug('invalid %s, clearing' % language)
                session['language'] = None
                language = browser_default
        else:
            language = browser_default
            #current_app.logger.debug('lang from browser: %s' % language)
        session['language'] = language #save it to session

        #and to user?
        return language

    # flask-login
    login_manager.login_view = 'frontend.login'
    login_manager.refresh_view = 'frontend.reauth'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)
    login_manager.setup_app(app)

    # flask-openid
    oid.init_app(app)

    # csrf for wtforms
    #from flask.ext.wtf import csrf
    csrf.init_app(app)
    
    # flask-restless
    rest.init_app(app, flask_sqlalchemy_db=db)
    restless_routes() #actually setup the routes

    # flask-admin
    admin = Admin(app, name='RootIO Backend', index_view=AdminHomeView())
    admin_routes(admin) #add flask-admin classes


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_messenger(app):
    try:
        # wrap zmq config in try/except, because it can fail easily
        app.messenger = zmq_context.socket(getattr(zmq,app.config['ZMQ_SOCKET_TYPE']))
        app.messenger.connect(app.config['ZMQ_BIND_ADDR'])
        app.logger.info('zmq connected %s' % app.config['ZMQ_BIND_ADDR'])

        # send startup message
        if app.debug:
            import time;
            time.sleep(1)
	    app.messenger.send('zmq {"status":"startup"}') 
    except zmq.error.ZMQError:
        app.logger.error('unable to start zmq')
        app.messenger = None


def configure_template_filters(app):

    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    #if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
    #    return

    import logging
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.DEBUG)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')

    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    app.logger.info("testing info.")
    app.logger.warn("testing warn.")
    app.logger.error("testing error.")

    if app.config.get('MAIL_SERVER'):
        mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                                   app.config['MAIL_USERNAME'],
                                   app.config['ADMINS'],
                                   'O_ops... %s failed!' % app.config['PROJECT'],
                                   (app.config['MAIL_USERNAME'],
                                    app.config['MAIL_PASSWORD']))
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
        )
        app.logger.addHandler(mail_handler)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500

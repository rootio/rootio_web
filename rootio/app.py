# -*- coding: utf-8 -*-
import json
import os
import threading
import time

import zmq
from flask import Flask, g, request, render_template, session
from flask.ext.admin import Admin
from flask.ext.babel import Babel
from sqlalchemy.exc import DatabaseError

from .admin import admin_routes, AdminHomeView
from .api import api, restless_routes
from .config import DefaultConfig
from .configuration import configuration
from .content import content, ContentMusic, ContentMusicArtist, ContentMusicAlbum
from .extensions import db, mail, cache, login_manager, oid, rest, csrf, zmq_context
from .frontend import frontend
from .messenger import messenger
from .onair import onair
from .radio import radio
from .rootio import rootio
from .settings import settings
from .telephony import telephony
from .user import User, user
from .utils import CustomJSONEncoder, make_dir

# For import *
#__all__ = ['create_app', 'music_file_uploads']
music_file_uploads = []

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
    configuration
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

    # @app.before_first_request
    # def handle_music_syncs():
    #     lock = threading.Lock()
    #     def handle_file():
    #         while True:
    #             lock.acquire()
    #             while len(music_file_uploads) > 0:
    #                 upload = music_file_uploads.pop(0)
    #                 process_music_data(upload[0], upload[1])
    #             lock.release()
    #             time.sleep(3)
    #
    #     thread = threading.Thread(target=handle_file())
    #     thread.start()

    return app


def get_dict_from_rows(rows):
    result = dict()
    for row in rows:
        result[row.title] = row
    return result


def process_music_data(station_id, json_string):
    songs_in_db = get_dict_from_rows(ContentMusic.query.filter(ContentMusic.station_id == station_id).all())
    artists_in_db = get_dict_from_rows(
        ContentMusicArtist.query.filter(ContentMusicArtist.station_id == station_id).all())
    albums_in_db = get_dict_from_rows(ContentMusicAlbum.query.filter(ContentMusicAlbum.station_id == station_id).all())

    data = json.loads(json_string)
    for artist in data:
        if artist in artists_in_db:
            music_artist = artists_in_db[artist]
        else:
            # persist the artist
            music_artist = ContentMusicArtist(**{'title': artist, 'station_id': station_id})
            artists_in_db[artist] = music_artist
            db.session.add(music_artist)
            try:
                db.session.commit()
            except DatabaseError:
                db.session.rollback()
                continue

        for album in data[artist]:
            if album in albums_in_db:
                music_album = albums_in_db[album]
            else:
                # persist the album
                music_album = ContentMusicAlbum(**{'title': album, 'station_id': station_id})
                albums_in_db[album] = music_album
                db.session.add(music_album)
                try:
                    db.session.commit()
                except DatabaseError:
                    db.session.rollback()
                    continue

            for song in data[artist][album]['songs']:
                if song['title'] in songs_in_db:
                    music_song = songs_in_db[song['title']]
                else:
                    music_song = ContentMusic(
                        **{'title': song['title'], 'duration': song['duration'], 'station_id': station_id,
                           'album_id': music_album.id, 'artist_id': music_artist.id})
                    songs_in_db[song['title']] = music_song
                db.session.add(music_song)
                try:
                    db.session.commit()
                except DatabaseError:
                    db.session.rollback()
                    continue


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    for directory in DefaultConfig.LOG_FOLDER, DefaultConfig.UPLOAD_FOLDER, DefaultConfig.OPENID_FS_STORE_PATH:
        make_dir(directory)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('rootio.cfg', silent=True)

    if config:
        app.config.from_object(config)

    # Use instance folder instead of env variables to make deployment easier.
    # app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)


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
        # TODO, first check user config?
        g.accept_languages = app.config.get('ACCEPT_LANGUAGES')
        accept_languages = g.accept_languages.keys()
        browser_default = request.accept_languages.best_match(accept_languages)
        if 'language' in session:
            language = session['language']
            # current_app.logger.debug('lang from session: %s' % language)
            if language not in accept_languages:
                # clear it
                # current_app.logger.debug('invalid %s, clearing' % language)
                session['language'] = None
                language = browser_default
        else:
            language = browser_default
            # current_app.logger.debug('lang from browser: %s' % language)
        session['language'] = language  # save it to session

        # and to user?
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
    # from flask.ext.wtf import csrf
    csrf.init_app(app)

    # flask-restless
    rest.init_app(app, flask_sqlalchemy_db=db)
    restless_routes()  # actually setup the routes

    # flask-admin
    admin = Admin(app, name='RootIO Backend', index_view=AdminHomeView())
    admin_routes(admin)  # add flask-admin classes


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_messenger(app):
    try:
        # wrap zmq config in try/except, because it can fail easily
        app.messenger = zmq_context.socket(getattr(zmq, app.config['ZMQ_SOCKET_TYPE']))
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

    # if app.debug or app.testing:
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
        return render_template("errors/forbidden_page.html", error=error), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html", error=error), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html", error=error), 500

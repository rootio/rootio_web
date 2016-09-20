# -*- coding: utf-8 -*-

import os, sys
import subprocess
import time
import json

from flask.ext.script import Manager, Shell

from rootio import create_app
from rootio.extensions import db

from rootio.radio import Station, Language
from rootio.telephony import Message, PhoneNumber
from rootio.user import User, UserDetail, ADMIN, ACTIVE
from rootio.utils import MALE

from alembic import command
from alembic.config import Config

def _make_context():
    from rootio.extensions import db
    import rootio.telephony as t
    import rootio.user as u
    import rootio.radio as r
    return dict(db=db, u=u.models, t=t.models, r=r.models)


app = create_app()
manager = Manager(app)
manager.add_command("sh", Shell(make_context=_make_context))


alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")


def easy():
    """ pre import some things """
    from rootio.extensions import db
    import rootio.telephony as t
    import rootio.user as u
    import rootio.radio as r

@manager.command
def run():
    """Run webserver for local development."""
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=8080)

@manager.command
def alembic():
    """Run in local machine."""
    subprocess.call(["venv/bin/alembic", "init", "alembic"])

@manager.command
def migrate(direction):
    """Migrate db revision"""
    if direction == "up":
        command.upgrade(alembic_config, "head")
    elif direction == "down":
        command.downgrade(alembic_config, "-1")

@manager.command
def migration(message):
    """Create migration file"""
    command.revision(alembic_config, autogenerate=True, message=message)

@manager.command
def stamp(revision):
    """Fake a migration to a particular revision"""
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, revision)

@manager.command
def reset_db():
    """Reset database"""

    print "WARNING: This will reset the database and may cause data loss."
    response = raw_input("Are you sure you want to continue? (Yes/No) ")
    if not response == "Yes":
        print "Aborted."
        sys.exit()

    db.drop_all()
    db.create_all()

    admin = User(
            name=u'admin',
            email=u'admin@example.com',
            password=u'123456',
            role_code=ADMIN,
            status_code=ACTIVE,
            user_detail=UserDetail(
                gender_code=MALE,
                age=25,
                url=u'http://example.com',
                location=u'Kampala',
                bio=u''))
    db.session.add(admin)

    english = Language(name="English",iso639_1="en",iso639_2="eng",locale_code="en_UG")
    db.session.add(english)
    luganda = Language(name="Luganda",iso639_1="lg",iso639_2="lug",locale_code="lg_UG")
    db.session.add(luganda)

    db.session.commit()
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, "head")

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

@manager.command
def drop_db_hard():
    #for when db.drop_all won't cut it, particularly with postgres on server

    print "WARNING: This will drop all database tables."
    response = raw_input("Are you sure you want to continue? (Yes/No) ")
    if not response == "Yes":
        print "Aborted."
        sys.exit()

    import sqlalchemy
    engine = sqlalchemy.create_engine('postgresql://postgres:NLPog1986@localhost')
    meta = sqlalchemy.MetaData(engine)
    meta.reflect()
    meta.drop_all()

@manager.command
def list_routes():
    import urllib
    from flask import url_for
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print line

@manager.command
def add_sms(data):
    data = json.loads(data)
    fr = checkNumber(data['fr'])
    to = checkNumber(data['to'])
    message = validate_sms(data['text'])
    sms = Message(message_uuid=data['uuid'], sendtime=data['time'], text=message, from_phonenumber_id=fr, to_phonenumber_id=to)
    db.session.add(sms)
    db.session.commit()

def checkNumber(num):
    from_phone = PhoneNumber.query.filter_by(number=num)
    if from_phone.count() == 1:
        num = from_phone[0].id
    else:
        phone = PhoneNumber(number=num,raw_number=num)
        db.session.add(phone)
        db.session.commit()
        num = phone.id
    return num

def validate_sms(message):
    message = message.replace("(", ",")
    message = message.replace(")", ",")  # removes the bug that makes FS send a bye signal do TTS server.
    message = message.replace("\n", " ")  # Remove the new line character people can envetually send and makes FS stop the TTS
    return message

if __name__ == "__main__":
    manager.run()


from flask.ext.script import Manager

from sms_server import app,db

manager = Manager(app)     

from rootio.extensions import db
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from rootio.telephony.models import *
from rootio.radio.models import *

@manager.command
def hello():
    print "hello"

@manager.command
def createdb():
    db.create_all()

@manager.command
def reloaddb():    
    db.drop_all()
    from rootio.telephony.models import PhoneNumber, Message
    db.create_all()


if __name__ == "__main__":
    manager.run()

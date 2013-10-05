
from flask.ext.script import Manager

from sms_server import app,db

manager = Manager(app)

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

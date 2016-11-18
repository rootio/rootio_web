import os 
import freeswitch

from rootio.config import DefaultConfig
from rootio.content.models import CommunityMenu, CommunityContent
from rootio.radio.models import Station
from rootio.telephony.models import PhoneNumber, Message
from freeswitch import *
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def do_bundle_purchase():
    os.system('python -m sms_server.bundle_robot')

def get_db_connection():
    engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
    return sessionmaker(bind=engine)()

def log_message(db, message, station_id):
    msg = Message()
    msg.sendtime = datetime.utcnow()
    msg.from_phonenumber = message.getHeader('from_user')
    msg.to_phonenumber = message.getHeader('to_user')
    msg.text = message.getBody()
    msg.station_id = station_id
    db._model_changes = {}
    db.add(msg)
    db.commit()

def chat(message, args):
    db = get_db_connection()
    station = db.query(Station).join(PhoneNumber, Station.cloud_phone).filter(PhoneNumber.raw_number==message.getHeader('to_user')).first()
    if station != None: #No station has the number that was called, exit, do not hangup
       log_message(db, message, station.id)
    txt = message.getBody()
    
    if 'bundle' in txt  and 'expired' in txt:
        pid = os.fork()
        if pid == 0: #Am a child :-)
            do_bundle_purchase()

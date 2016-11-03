import os

from rootio.config import DefaultConfig
from rootio.content.models import CommunityMenu, CommunityContent
from rootio.radio.models import Station
from rootio.telephony.models import PhoneNumber
from freeswitch import *
from datetime import datetime, timedelta
from ofs.local import PTOFS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 

def get_message_category(session, prompt):
    i = 0
    digits = '0'
    #session.speak('Welcome. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)))
    digits = session.playAndGetDigits(1, 1, 3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)),"","[123]") 
    return digits

def get_validity(session, prompt):
    i = 0 
    digits = '0'
    digits = session.playAndGetDigits(1, 2, 3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)),"","")
    return digits
    

def record_message(session, prompt, filename, station_id, category_id, maxLength=30, maxSilence=5, audibleThreshold=0):
    #session.speak("Please record your message now followed by the hash key")
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)))
    session.setInputCallback(input_callback)
    if not os.path.exists("{0}/{1}/{2}/{3}".format(DefaultConfig.CONTENT_DIR, "community-content",station_id,category_id)):
        os.makedirs("{0}/{1}/{2}/{3}".format(DefaultConfig.CONTENT_DIR, "community-content",station_id,category_id))
    starttime = datetime.utcnow()
    session.recordFile("{0}/{1}/{2}/{3}/{4}".format(DefaultConfig.CONTENT_DIR, "community-content",station_id,category_id, filename), maxLength, audibleThreshold, maxSilence)
    return (datetime.utcnow() - starttime).seconds

def confirm_action(session, prompt):
    
    digits = session.playAndGetDigits(1,1,3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)),"","[123]")
    return digits

def play_back_recording(session, filename, station_id, category_id):
    session.consoleLog("info", str(os.path.join(DefaultConfig.CONTENT_DIR, "community-content", str(station_id),category_id,filename)))
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, "community-content", str(station_id),category_id,filename)))
         
def delete_recording(session, filename):
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, "community-content", filename)))

def input_callback(session, event, obj):
    if event == "dtmf" and obj.digit == "#":
        return 'break'  
  
def get_filename(from_number):
    now = datetime.utcnow()
    tstr = now.strftime("%Y%m%d%H%M%S")    
    return "{0}_{1}.wav".format(tstr,from_number)

def confirmation(session, prompt, filename,duration, validity, station_id, category, db):
    action = confirm_action(session, prompt)
    if action == None or action == '':
        session.hangup()
        return
    #Listening to the message
    if action == '1':
        play_back_recording(session, filename, station_id, category)
        confirmation(session, prompt, filename, validity, station_id, category, db)
    #saving the message
    elif action == '2':
        content = CommunityContent()
        content.station_id =  station_id
        content.originator = session.getVariable('caller_id_number')
        content.message = filename
        content.date_created = datetime.utcnow()
        content.duration = duration
        content.type_code =  category
        content.valid_until = datetime.utcnow() + timedelta(int(validity)) 
        db._model_changes = {}
        db.add(content)
        db.commit()
    #discarding the message
    elif action == '3':
        delete_recording(session, filename)

def get_db_connection():
    engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
    return sessionmaker(bind=engine)()


def handler(session, args):
    session.answer()
    session.consoleLog("info", DefaultConfig.SQLALCHEMY_DATABASE_URI)
    session.set_tts_params("flite", "kal")
    
    db = get_db_connection()
    station = db.query(Station).join(PhoneNumber, Station.cloud_phone).filter(PhoneNumber.raw_number==session.getVariable('destination_number')).first()
    if station == None: #No station has the number that was called, exit, do not hangup
       return

    community_menu = db.query(CommunityMenu).filter(CommunityMenu.station_id == station.id).first()
    
    session.consoleLog("info", str(community_menu.message_type_prompt))
    message_category = get_message_category(session, community_menu.message_type_prompt)
    if message_category == None or message_category == '':
        session.hangup()
        return
    if message_category == '3': #greetings have a duration of one day
        validity_days = '1'
    else:     
        validity_days = get_validity(session, community_menu.days_prompt)
    if validity_days == None or validity_days == '':
        session.hangup()
        return
    filename = get_filename(session.getVariable('caller_id_number'))
    duration = record_message(session, community_menu.record_prompt, filename, community_menu.station_id, message_category)
    confirmation(session, community_menu.finalization_prompt, filename, duration, validity_days, community_menu.station_id,  message_category, db) 

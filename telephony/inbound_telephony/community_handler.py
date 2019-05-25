import os
from datetime import datetime, timedelta

from rootio.config import DefaultConfig
from rootio.content.models import CommunityMenu, CommunityContent
from rootio.radio.models import Station
from rootio.telephony.models import PhoneNumber, Call
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_message_category(session, prompt):
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)))
    digits = session.playAndGetDigits(1, 1, 3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)),
                                      "", "[123]")
    return digits


def get_validity(session, prompt):
    digits = session.playAndGetDigits(1, 2, 3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)), "", "")
    return digits


def record_message(session, prompt, filename, station_id, category_id, max_length=30, max_silence=5,
                   audible_threshold=0):
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)))
    session.setInputCallback(input_callback)
    if not os.path.exists("{0}/{1}/{2}/{3}".format(DefaultConfig.CONTENT_DIR, "community-content", station_id,
                                                   category_id)):
        os.makedirs("{0}/{1}/{2}/{3}".format(DefaultConfig.CONTENT_DIR, "community-content", station_id, category_id))
    start_time = datetime.utcnow()
    session.recordFile("{0}/{1}/{2}/{3}/{4}".format(DefaultConfig.CONTENT_DIR, "community-content", station_id,
                                                    category_id, filename), max_length, audible_threshold, max_silence)
    os.chmod(filename, 0755)
    return (datetime.utcnow() - start_time).seconds


def confirm_action(session, prompt):
    digits = session.playAndGetDigits(1, 1, 3, 5000, "*#", str(os.path.join(DefaultConfig.CONTENT_DIR, prompt)), "",
                                      "[123]")
    return digits


def play_back_recording(session, filename, station_id, category_id):
    session.consoleLog("info", str(
        os.path.join(DefaultConfig.CONTENT_DIR, "community-content", str(station_id), category_id, filename)))
    session.streamFile(
        str(os.path.join(DefaultConfig.CONTENT_DIR, "community-content", str(station_id), category_id, filename)))


def delete_recording(session, filename):
    session.streamFile(str(os.path.join(DefaultConfig.CONTENT_DIR, "community-content", filename)))


def input_callback(event, obj):
    if event == "dtmf" and obj.digit == "#":
        return 'break'


def get_filename(from_number):
    now = datetime.utcnow()
    tstr = now.strftime("%Y%m%d%H%M%S")
    return "{0}_{1}.wav".format(tstr, from_number)


def confirmation(session, prompt, filename, duration, validity, station_id, category, db):
    action = confirm_action(session, prompt)
    if action is None or action == '':
        return
    # Listening to the message
    if action == '1':
        play_back_recording(session, filename, station_id, category)
        confirmation(session, prompt, filename, duration, validity, station_id, category, db)
    # saving the message
    elif action == '2':
        content = CommunityContent()
        content.station_id = station_id
        content.originator = session.getVariable('caller_id_number')
        content.message = filename
        content.date_created = datetime.utcnow()
        content.duration = duration
        content.type_code = category
        content.valid_until = datetime.utcnow() + timedelta(int(validity))
        db._model_changes = {}
        db.add(content)
        db.commit()
    # discarding the message
    elif action == '3':
        delete_recording(session, filename)


def get_db_connection():
    engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
    return sessionmaker(bind=engine)()


def log_call(start_time, db, session, station_id):
    call = Call()
    call.call_uuid = session.getVariable('uuid')
    call.start_time = start_time
    call.duration = (datetime.utcnow() - start_time).seconds
    call.from_phonenumber = session.getVariable('caller_id_number')
    call.to_phonenumber = session.getVariable('destination_number')
    call.station_id = station_id
    db._model_changes = {}
    db.add(call)
    db.commit()


def finish(answer_time, db, session, station_id):
    log_call(answer_time, db, session, station_id)
    session.hangup()


def handler(session, args):
    session.consoleLog("info", session.__dict__)
    session.answer()
    answer_time = datetime.utcnow()
    session.set_tts_params("flite", "kal")

    db = get_db_connection()
    station = db.query(Station).filter(Station.incoming_gateways.number_bottom == session.getVariable('destination_number')).first()
    if station is None:  # No station has the number that was called, exit, do not hangup
        return

    community_menu = db.query(CommunityMenu).filter(CommunityMenu.station_id == station.id).first()

    session.consoleLog("info", str(community_menu.message_type_prompt))
    message_category = get_message_category(session, community_menu.message_type_prompt)
    if message_category is None or message_category == '':
        finish(answer_time, db, session, station.id)
        return
    if message_category == '3':  # greetings have a duration of one day
        validity_days = '1'
    else:
        validity_days = get_validity(session, community_menu.days_prompt)
    if validity_days is None or validity_days == '':
        finish(answer_time, db, session, station.id)
        return
    filename = get_filename(session.getVariable('caller_id_number'))
    duration = record_message(session, community_menu.record_prompt, filename, community_menu.station_id,
                              message_category)
    confirmation(session, community_menu.finalization_prompt, filename, duration, validity_days,
                 community_menu.station_id, message_category, db)
    finish(answer_time, db, session, station.id)

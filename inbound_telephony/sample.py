import os
from freeswitch import *
from datetime import datetime
from ofs.local import PTOFS

station_lines = {'1001':'10', '1003':'11', '1005':'12','1007':'13'}
station_welcome_prompts = {'10':'welcome_aber.mp3', '11':'welcome_pabbo.mp3', '12':'welcome_kitgum.mp3', '13':'welcome_patongo.mp3'}
station_validity_prompts = {'10':'ad_validity.mp3', '11':'ad_validity.mp3','12':'ad_validity.mp3','13':'ad_validity.mp3'}
station_recording_prompts = {'10':'to_record.mp3', '11':'to_record.mp3','12':'to_record.mp3','13':'to_record.mp3'}
station_confirmation_prompts = {'10':'to_confirm.mp3', '11':'to_confirm.mp3','12':'to_confirm.mp3','13':'to_confirm.mp3'}
station_message_saved_messages = {'10':'recording_saved.mp3','11':'recording_saved.mp3','12':'recording_saved.mp3','13':'recording_saved.mp3'}
station_message_discarded = {'10':'recording_deleted.mp3','11':'recording_deleted.mp3','12':'recording_deleted.mp3','13':'recording_deleted.mp3'}
station_no_input_received_prompts = {'10':'no_input_received.mp3','11':'no_input_received.mp3','12':'no_input_received.mp3','13':'no_input_received.mp3'}
station_no_input_received_goodbye = {'10':'no_input_received.mp3','11':'no_input_received.mp3','12':'no_input_received.mp3','13':'no_input_received.mp3'}
base_files_directory = "/home/amour/media/gdrive/Community Media/data" 
base_prompts_directory = "/home/amour/media/gdrive/IVR Prompts"
message_categories = {"1":"advertisements", "2":"announcements", "3":"greetings"} 

def get_message_category(session):
    i = 0
    digits = '0'
    #session.speak('Welcome. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_welcome_prompts[station_lines[session.getVariable('destination_number')]]))
    digits = session.playAndGetDigits(1, 1, 3, 5000, "*#", "{0}/{1}".format(base_prompts_directory, station_recording_prompts[station_lines[session.getVariable('destination_number')]]),"","[123]") 
    return digits

def get_validity(session):
    i = 0 
    digits = '0'
    digits = session.playAndGetDigits(1, 2, 3, 5000, "*#", "{0}/{1}".format(base_prompts_directory, station_validity_prompts[station_lines[session.getVariable('destination_number')]]),"","")
    return digits
    

def record_message(session, filename, maxLength, maxSilence, audibleThreshold):
    #session.speak("Please record your message now followed by the hash key")
    session.streamFile("/home/amour/media/start_recording.wav")
    session.setInputCallback(input_callback)
    session.recordFile("{0}/{1}".format(base_files_directory, filename), maxLength, audibleThreshold, maxSilence)

def confirm_action(session):
    digits = session.playAndGetDigits(1,1,3, 5000, "*#", "{0}/{1}".format(base_prompts_directory, station_confirmation_prompts[station_lines[session.getVariable('destination_number')]]),"","[123]")
    return digits

def play_back_recording(session, filename):
    session.streamFile("{0}/{1}".format(base_files_directory, filename))
         
def delete_recording(session, filename):
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_message_discarded_messages[station_lines[session.getVariable('destination_number')]]))

def input_callback(session, event, obj):
    if event == "dtmf" and obj.digit == "#":
        return 'break'  
  
def get_filename(from_number):
    now = datetime.utcnow()
    tstr = now.strftime("%Y%m%d%H%M%S")    
    return "{0}_{1}.wav".format(tstr,from_number)

def save_to_ofs(session, filename, validity, station_id, category):
    o = PTOFS(storage_dir = "/home/amour/media/gdrive/Community Media/data")
    bucket_id = "{0}_{1}".format(station_id, category)
    session.consoleLog("info", "bucket id is " + bucket_id)
    result = o.put_stream(bucket_id, filename, open("{0}/{1}".format(base_files_directory, filename)), params={"validity":validity})   
    session.consoleLog("info", str(result))    
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_message_saved_messages[station_lines[session.getVariable('destination_number')]]))

def confirmation(session, filename, validity, station_id, category):
    action = confirm_action(session)
    if action == None or action == '':
        session.hangup()
        return
    #Listening to the message
    if action == '1':
        play_back_recording(session, filename)
        confirmation(session, filename, validity, station_id, category)
    #saving the message
    elif action == '2':
        save_to_ofs(session, filename, validity, station_id, category)
    #discarding the message
    elif action == '3':
        delete_recording(session, filename)

def handler(session, args):
    session.answer()
    session.consoleLog("info", "we got a call from Jude")
    session.set_tts_params("flite", "kal")
    message_category = get_message_category(session)
    if message_category == None or message_category == '':
        session.hangup()
        return
    if message_category == '3': #greetings have a duration of one day
        validity_days = '1'
    else:     
        validity_days = get_validity(session)
    if validity_days == None or validity_days == '':
        session.hangup()
        return
    filename = get_filename(session.getVariable('caller_id_number'))
    record_message(session, filename, 150, 0, 0)
    confirmation(session, filename, validity_days, station_lines[session.getVariable('destination_number')],  message_category) 

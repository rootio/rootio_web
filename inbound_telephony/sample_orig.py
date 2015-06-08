import os
from freeswitch import *
from datetime import datetime
from ofs.local import PTOFS

station_lines = {'1001':'10', '1003':'11', '1005':'12','1007':'13'}
station_welcome_prompts = {'10':'welcome_aber.mp3', '11':'welcome_pabbo.mp3', '12':'welcome_kitgum.mp3', '13':'welcome_patongo.mp3'}
station_validity_prompts = dict()
station_recording_prompts = {'10':'to_record.mp3', '11':'to_record.mp3','12':'to_record.mp3','13':'to_record.mp3'}
station_confirmation_prompts = {'10':'to_confirm.mp3', '11':'to_confirm.mp3','12':'to_confirm.mp3','13':'to_confirm.mp3'}
station_message_saved_messages = {'10':'recording_saved.mp3','11':'recording_saved.mp3','12':'recording_saved.mp3','13':'recording_saved.mp3'}
station_message_discarded = {'10':'recording_deleted.mp3','11':'recording_deleted.mp3','12':'recording_deleted.mp3','13':'recording_deleted.mp3'}
station_no_input_received_prompts = {'10':'no_input_received.mp3','11':'no_input_received.mp3','12':'no_input_received.mp3','13':'no_input_received.mp3'}
station_no_input_received_goodbye = {'10':'no_input_received.mp3','11':'no_input_received.mp3','12':'no_input_received.mp3','13':'no_input_received.mp3'}
base_files_directory = "/home/amour/media/gdrive/Community Media" 
base_prompts_directory = "/home/amour/media/gdrive/IVR Prompts"
message_categories = {"1":"advertisements", "2":"announcements", "3":"greetings"} 

def get_message_category(session):
    i = 0
    digits = '0'
    #session.speak('Welcome. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_welcome_prompts[station_lines[session.getVariable('destination_number')]]))
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_recording_prompts[station_lines[session.getVariable('destination_number')]]))
    while i <= 3:
        digits = session.getDigits(100,"#",50000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                #session.speak("No input has been received. Goodbye")
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]]))
                return
            else:
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]]))
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_recording_prompts[station_lines[session.getVariable('destination_number')]]))
                #session.speak("No input received. Please enter an option")
                i = i+1
        else:
            if digits in ["1","2","3"]:
                return digits
            else:
                #session.speak('Invalid option selected. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')
                session.speak('Invalid option selected')
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_welcome_prompts[station_lines[session.getVariable('destination_number')]]))

def get_validity(session):
    i = 0 
    digits = '0'
    session.speak('Please enter the number of days for which this advertisement is valid')
    while i <= 3:
        digits = session.getDigits(1,"#",5000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                #session.speak("No input has been received. Goodbye")
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]])) 
                return
            else:
                #session.speak("No input received. Please enter an option")
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]]))
                session.speak('Please enter the number of days for which this advertisement is valid')
                i = i+1
        else:
            return digits
    

def record_message(session, filename, maxLength, maxSilence, audibleThreshold):
    session.speak("Please record your message now followed by the hash key")
    session.setInputCallback(input_callback)
    session.recordFile("{0}/{1}".format(base_files_directory, filename), maxLength, audibleThreshold, maxSilence)

def confirmation(session, filename, validity, station_id, message_category):
    i = 0
    #session.speak("To listen to this message press 1, to save this message press 2,  to discard this message press 3")
    session.streamFile("{0}/{1}".format(base_prompts_directory, station_confirmation_prompts[station_lines[session.getVariable('destination_number')]]))
    while i <= 3:
        digits = session.getDigits(1,"#",5000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                #session.speak("No input has been received. Goodbye")
                session.streamFile("{0}/{1}".format({base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]]}))
                return
            else:
                #session.speak("No input received. Please enter an option")
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_no_input_received_prompts[station_lines[session.getVariable('destination_number')]]))
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_confirmation_prompts[station_lines[session.getVariable('destination_number')]]))
                i = i+1
        else:
            if str(digits) == '1':
                session.streamFile("{0}/{1}".format(base_files_directory,filename))
                confirmation(session, filename, validity, station_id, message_category)
                break
            elif str(digits) == '2':
                save_to_ofs(session, filename, validity, station_id, message_category)
                #session.speak('Your recording has been saved. Thank you')
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_message_saved_messages[station_lines[session.getVariable('destination_number')]]))
                break
            elif str(digits) == '3': 
                #session.speak('Your recording was erased. Good bye')
                session.streamFile("{0}/{1}".format(base_prompts_directory, station_message_discarded_messages[station_lines[session.getVariable('destination_number')]]))
                break

def input_callback(session, event, obj):
    if event == "dtmf" and obj.digit == "#":
        return 'break'    

def get_filename(from_number):
    now = datetime.utcnow()
    tstr = now.strftime("%Y%m%d%H%M%S")    
    return "{0}_{1}.wav".format(tstr,from_number)

def save_to_ofs(session, filename, validity, station_id, category):
    o = PTOFS()
    bucket_id = "{0}_{1}".format(station_id, category)
    session.consoleLog("info", "bucket id is " + bucket_id)
    result = o.put_stream(bucket_id, filename, open("{0}/{1}".format(base_files_directory, filename)), params={"validity":validity})   
    session.consoleLog("info", str(result))    

def handler(session, args):
    session.answer()
    session.consoleLog("info", "we got a call from Jude")
    session.set_tts_params("flite", "kal")
    message_category = get_message_category(session)
    validity_days = get_validity(session)
    filename = get_filename(session.getVariable('caller_id_number'))
    record_message(session, filename, 30, 0, 1)
    confirmation(session, filename, validity_days, 1, message_categories[message_category])
    

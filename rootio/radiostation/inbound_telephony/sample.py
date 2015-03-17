import os
from freeswitch import *
from datetime import datetime
from ofs.local import PTOFS

station_lines = {'1003':'1'}
station_welcome_prompts = dict()
station_validity_prompts = dict()
station_recording_prompts = dict()
station_confirmation_prompts = dict()
station_message_saved_messages = dict()
station_message_discarded = dict()
station_no_input_received_prompts = dict()
station_no_input_received_goodbye = dict()
base_files_directory = "/home/amour" 
message_categories = {"1":"advertisements", "2":"announcements", "3":"greetings"} 

def get_message_category(session):
    i = 0
    digits = '0'
    session.speak('Welcome. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')
    while i <= 3:
        digits = session.getDigits(1,"#",5000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                session.speak("No input has been received. Goodbye")
                return
            else:
                session.speak("No input received. Please enter an option")
                i = i+1
        else:
            if digits in ["1","2","3"]:
                return digits
            else:
                 session.speak('Invalid option selected. To leave an advertisement, press 1. To leave an announcement, press 2. To leave a greeting, press 3')


def get_validity(session):
    i = 0 
    digits = '0'
    session.speak('Please enter the number of days for which this advertisement is valid')
    while i <= 3:
        digits = session.getDigits(1,"#",5000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                session.speak("No input has been received. Goodbye")
                return
            else:
                session.speak("No input received. Please enter an option")
                i = i+1
        else:
            return digits
    

def record_message(session, filename, maxLength, maxSilence, audibleThreshold):
    session.speak("Please record your message now")
    session.setInputCallback(input_callback)
    session.recordFile("{0}/{1}".format(base_files_directory, filename), maxLength, audibleThreshold, maxSilence)

def confirmation(session, filename, validity, station_id, message_category):
    i = 0
    session.speak("To listen to this message press 1, to save this message press 2,  to discard this message press 3")
    while i <= 3:
        digits = session.getDigits(1,"#",5000)
        session.consoleLog("info","DTMF digit is {0}".format(digits))
        if digits == None or digits == '':
            if i == 3:
                session.speak("No input has been received. Goodbye")
                return
            else:
                session.speak("No input received. Please enter an option")
                i = i+1
        else:
            if str(digits) == '1':
                session.streamFile("{0}/{1}".format(base_files_directory,filename))
                confirmation(session, filename, validity, station_id, message_category)
                break
            elif str(digits) == '2':
                save_to_ofs(session, filename, validity, station_id, message_category)
                session.speak('Your recording has been saved. Thank you')
                break
            elif str(digits) == '3': 
                session.speak('Your recording was erased. Good bye')
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
    

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 1:50:35 PM$"

from rootio.config import *
from rootio.radio.models import Station
from call_handler import CallHandler
from program_handler import ProgramHandler
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import time
import threading
import json

from rootio.extensions import db
telephony_server = Flask("ResponseServer")
telephony_server.debug = True
telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost/rootio'

db = SQLAlchemy(telephony_server)

class RadioStation(Station):
    #programs Loaded by super class init
    #Telephony lines loaded by super class init
    #Load a definition for station IVR if any
    #Initiate a listener for calls
    #Sit and wait for a call to close
    
    __call_handler = None
    __program_handler = None
    id = None
    station = None
    __call_requester = None
    __available_calls = dict()
    __call_answer_info = dict() 
    
    def run(self):
        #self.__call_handler.run()
        self.__call_handler = CallHandler(self)
        self.__program_handler = ProgramHandler(db, self)
        self.__program_handler.run()
        while True:
            time.sleep(1)
        return
    
    def stop(self):
        self.__call_handler.stop()
        self.__program_handler.stop()
        pass
    
    def handle_incoming_call(self):
       #if target of the call is station, this handles. else pass it to program handler
        return

    def notify_call_answered(self, answer_info):
        self.__in_call = True
        answer_info_json = json.loads(answer_info.serialize('json'))
        self.__call_answer_info[answer_info_json['Caller-Destination-Number']] = answer_info
        self.__call_requester.notify_call_answered(answer_info)
    
    def request_call(self, program_action, to_numbers, action, argument, duration):
        self.__call_requester = program_action
        if not to_numbers in self.__available_calls:
            print "calling out..."
            result = self.__call_handler.call(to_numbers, action, argument, duration)
            self.__available_calls[to_numbers] = result
        else: 
            t = threading.Thread(target=self.notify_call_answered, args=(self.__call_answer_info[to_numbers],))
            t.daemon = True
            t.start()
        print self.__available_calls
        return self.__available_calls[to_numbers]

    def hangup_call(self, to_number):
        del self.__available_calls[to_number]
        call_json = json.loads(self.__call_answer_info[to_number].serialize('json'))
        return self.__call_handler.hangup(call_json['Channel-Call-UUID'])
    
    def play_to_call(self, content_location, call_UUID):
        return self.__call_handler.play(content_location, call_UUID)

    def stop_playback(self, call_UUID, content_location):
        return self.__call_handler.stop_play(call_UUID, content_location)    

    def speak_to_call(self, phrase, call_UUID):
        return self.__call_handler.speak(phrase, call_UUID)

    def request_conference(self, call_UUID, conference_UUID):
        return self.__call_handler.request_conference(call_UUID, conference_UUID)

    def notify_incoming_dtmf(self, dtmf_info):
        self.__call_requester.handle_dtmf(dtmf_info)
        print "JSON from DTMF coming in "

    def register_for_media_playback_stop(self, recipient, from_number):
        self.__call_handler.register_for_media_playback_stop(recipient, from_number)
    
    def notify_media_play_stop(self, media_stop_info):
        self.__call_requester.handle_media_play_stop(media_stop_info)

    def listen_for_media_play_stop(self):
        self.__call_handler.listen_for_media_play_stop()
 
    def __init__(self, station_id):
        self.id = station_id
        self.station = db.session.query(Station).filter(Station.id == station_id).one()
        print self.station.name
        return

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
    __call_answer_info = 'nothing'
    
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
        self.__call_answer_info = answer_info
        self.__call_requester.notify_call_answered(answer_info)
    
    def request_call(self, program_action, to_numbers, action, argument, duration):
        self.__call_requester = program_action
        if not to_numbers in self.__available_calls:
            print "calling out..."
            result = self.__call_handler.call(to_numbers, action, argument, duration)
            self.__available_calls[to_numbers] = result
        else: 
            t = threading.Thread(target=self.notify_call_answered, args=(self.__call_answer_info,))
            t.daemon = True
            t.start()
        return self.__available_calls[to_numbers]

    def terminate_call(self, call_UUID):
        return self.__call_handler.hangup(call_UUID)
    
    def play_to_call(self, content_location, call_UUID):
        return self.__call_handler.play(content_location, call_UUID)
    
    def speak_to_call(self, phrase, call_UUID):
        return self.__call_handler.speak(phrase, call_UUID)

    def request_conference(self, call_UUID, conference_UUID):
        return self.__call_handler.request_conference(call_UUID, conference_UUID)

    def __init__(self, station_id):
        self.id = station_id
        self.station = db.session.query(Station).filter(Station.id == station_id).one()
        print self.station.name
        return
        
    
        
    
        
    
    
    

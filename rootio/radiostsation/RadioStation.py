# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 1:50:35 PM$"

from rootio.config import *
from rootio.radio.models import Station
from CallHandler import CallHandler
from ProgramHandler import ProgramHandler
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import time

from rootio.extensions import db
telephony_server = Flask("ResponseServer")
telephony_server.debug = True
telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost'

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
    
    def request_call(self, to_numbers, action, argument, duration):
        print "calling out..."
        return self.__call_handler.call(to_numbers, action, argument, duration)
    
    def terminate_call(self, call_UUID):
        return self.__call_handler.terminate_call(call_UUID)
    
    def play_to_call(self, content_location, call_UUID):
        return self.__call_handler.play_to_call(content_location, call_UUID)
    
    def speak_to_call(self, phrase, call_UUID):
        return self.__call_handler.speak_to_call(phrase, call_UUID)

    def __init__(self, station_id):
        self.id = station_id
        self.station = db.session.query(Station).filter(Station.id == station_id).one()
        print self.station.name
        return
        
    
        
    
        
    
    
    

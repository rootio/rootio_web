# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 1:50:35 PM$"

from rootio.config import *
from rootio.radio.models import Station
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
    

    def __init__(self, station_id):
        self.__id = station_id
        self.station = db.session.query(Station).filter(Station.id == station_id).one()
        print self.station.name
        #self.__call_handler = new CallHandler(self, self.)
        self.__program_handler = ProgramHandler(db, self.station)
        return
        
    
        
    def run(self):
        #self.__call_handler.run()
        self.__program_handler.run()
        while True:
            time.sleep(1)
        return
    
    def stop(self):
        self.__call_handler.stop()
        self.__program_handler.stop()
        pass
    
    def handle_incoming_call(self,):
        #if target of the call is station, this handles. else pass it to program handler
        pass;
    
    
    

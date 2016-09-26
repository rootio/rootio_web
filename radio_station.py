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
import logging
from rootio.extensions import db

telephony_server = Flask("ResponseServer")
telephony_server.debug = True
telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost/rootio'


class RadioStation(Station):
 
    def run(self):
        self.call_handler = CallHandler(self, telephony_server.config)
        self.__program_handler = ProgramHandler(self.db, self)
        self.__program_handler.run()
        while True:
            time.sleep(1)
        return
    
    def stop(self):
        self.call_handler.stop()
        self.__program_handler.stop()
        pass
    
    def __init__(self, station_id, logger):
        self.id = station_id
        self.logger = logger
        self.db = SQLAlchemy(telephony_server)
        self.station = self.db.session.query(Station).filter(Station.id == station_id).one()
        self.logger.info("Starting up station {0}".format(self.station.name))
        return

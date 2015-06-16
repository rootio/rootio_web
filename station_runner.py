# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 4:16:15 PM$"

from rootio.config import *
from rootio.radio.models import Station
from call_handler import CallHandler
from radio_station import RadioStation
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import threading

from rootio.extensions import db
telephony_server = Flask("ResponseServer")
telephony_server.debug = True
telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost/rootio'





if __name__ == "__main__":
    db = SQLAlchemy(telephony_server)
    stations = db.session.query(Station).all()
    for station in stations:
        radio_station = RadioStation(station.id)
        print 'launching station : {0}'.format(station.id)
        t = threading.Thread(target=radio_station.run, args=())
        t.start()
     
    print "================ service started at {0} ==============".format(datetime.utcnow())

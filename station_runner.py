# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 4:16:15 PM$"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import threading
import logging
from logging.handlers import TimedRotatingFileHandler


from radio_station import RadioStation
from rootio.radio.models import Station
from rootio.config import DefaultConfig





if __name__ == "__main__":
    #setup logging
    app_logger = logging.getLogger('station_runner')
    hdlr = TimedRotatingFileHandler('/var/log/rootio/stations.log',when='midnight',interval=1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    app_logger.addHandler(hdlr)
    app_logger.setLevel(logging.DEBUG)    

    engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    stations = session.query(Station).all()
    for station in stations:
    #    if station.id == 15:
            radio_station = RadioStation(station.id, session, app_logger)
            app_logger.info('launching station : {0}'.format(station.id))
            t = threading.Thread(target=radio_station.run, args=())
            t.start()
     
    print "================ service started at {0} ==============".format(datetime.utcnow())


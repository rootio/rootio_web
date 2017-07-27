# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 4:16:15 PM$"

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import threading
import logging
from logging.handlers import TimedRotatingFileHandler


from radio_station import RadioStation
from rootio.radio.models import Station
from rootio.config import DefaultConfig


from daemoner import Daemon
from datetime import datetime
import zmq
import socket
import json 


class StationRunner(Daemon):

    def run(self):
        self.__logger = logging.getLogger('station_runner')
        hdlr = TimedRotatingFileHandler('/var/log/rootio/stations.log',when='midnight',interval=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.__logger.addHandler(hdlr)
        self.__logger.setLevel(logging.DEBUG)

        #set up scheduling 
        lst_thr = threading.Thread(target=self.__start_listener, args=())
        lst_thr.start()       

        engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
        session = sessionmaker(bind=engine)()
        stations = session.query(Station).all()

        for station in stations:
            radio_station = RadioStation(station.id, session, self.__logger)
            self.__logger.info('launching station : {0}'.format(station.id))
            t = threading.Thread(target=radio_station.run, args=())
            t.start()
        print "================ service started at {0} ==============".format(datetime.utcnow())

    def __start_listener(self):
        self.__station_sockets = dict()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((DefaultConfig.SCHEDULE_EVENTS_SERVER_IP, DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))
        s.listen(0)
        self.__logger.info("Started TCP listener on port {0}".format(DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))

        while 1:
            cli, adr = s.accept()
            thrd = threading.Thread(target=self.__handle_tcp_connection, args=(cli,))
            thrd.daemon = True
            thrd.start()

        
    def __handle_tcp_connection(self, sck): #TODO: handle json errors, else server will break due to rogue connection        
        while True:
            data = sck.recv(1024)
            print data
            event = json.loads(data)
            if event["action"] == "register": #A station socket is registering
                self.__station_sockets[event["station"]] = sck
                self.__logger.info("Station {0} has registered for schedule change events".format(event["station"]))
            elif event["action"] in ["add","delete","update"]: #The schedule is alerting us of a change
                if event["station"] in self.__station_sockets:
                    self.__station_sockets[event["station"]].send(data)
                    self.__logger.info("Event of type {0} sent to station {1} on scheduled program {2}".format(event["action"], event["station"], event["id"]))
        


if __name__ == "__main__":
    station_daemon = StationRunner("/tmp/station_runner.pid")
    if(len(sys.argv) == 2):
        if sys.argv[1] == "start":
            station_daemon.start()
        elif sys.argv[1] == "stop":
            station_daemon.stop()
        elif sys.argv[1] == "restart": 
            station_daemon.restart()
        else:
            print "Wrong arguments supplied. Usage: station_runner start|stop|restart"
    else:
        print "Wrong number of arguments supplied. Usage: station_runner start|stop|restart"         
         

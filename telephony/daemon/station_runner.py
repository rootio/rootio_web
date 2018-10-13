import json
import logging
import os
import socket
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import threading
from datetime import datetime
import time
from logging.handlers import TimedRotatingFileHandler

from rootio.config import DefaultConfig
from rootio.radio.models import Station
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from daemoner import Daemon
from ..radio_station import RadioStation


class StationRunner(Daemon):

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        Daemon.__init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
        self.logger = logging.getLogger('station_runner')

    def run(self):
        log_folder = DefaultConfig.LOG_FOLDER
        hdlr = TimedRotatingFileHandler(os.path.join(log_folder, 'stations.log'), when='midnight', interval=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.DEBUG)

        # set up scheduling
        lst_thr = threading.Thread(target=self.__start_listener, args=())
        lst_thr.start()

        try:
            engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
            session = sessionmaker(bind=engine)()
            stations = session.query(Station).all()
        except Exception as e:
            self.logger.error(e.message)
            return

        for station in stations:
            radio_station = RadioStation(station, session, self.logger)
            self.logger.info('launching station : {0}'.format(station.id))
            t = threading.Thread(target=radio_station.run, args=())
            t.start()
        self.logger.info(
            '================ Station runner service started at {0} =============='.format(datetime.utcnow()))

    def __start_listener(self):
        self.__station_sockets = dict()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # On restart, socket may be in TIME_WAIT from previous stop, need to try multiple times to bind
        bound = False
        while not bound:
            try:
                s.bind((DefaultConfig.SCHEDULE_EVENTS_SERVER_IP, DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))
                bound = True
            except:
                self.logger.error("Error on server bind, retrying. Retrying in 30 secs...")
                time.sleep(30)
        s.listen(0)
        self.logger.info("Started TCP listener on port {0}".format(DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))

        while 1:
            cli, adr = s.accept()
            thrd = threading.Thread(target=self.__handle_tcp_connection, args=(cli,))
            thrd.daemon = True
            thrd.start()

    def __handle_tcp_connection(self, sck):  # TODO: handle json errors, else server will break due to rogue connection
        data = sck.recv(1024)
        try:
            event = json.loads(data)
        except ValueError as e:
            return

        if "action" in event and "station" in event:
            if event["action"] == "register":  # A station is registering
                self.__station_sockets[event["station"]] = sck
                self.logger.info("Station {0} has registered for schedule change events".format(event["station"]))
            elif event["action"] in ["add", "delete", "update"] and "id" in event:  # Schedule is alerting of a change
                if event["station"] in self.__station_sockets:
                    self.__station_sockets[event["station"]].send(data)
                    self.logger.info("Event of type {0} sent to station {1} on scheduled program {2}"
                                     .format(event["action"], event["station"], event["id"]))


if __name__ == "__main__":
    station_daemon = StationRunner("/tmp/station_runner.pid")
    if len(sys.argv) == 2:
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

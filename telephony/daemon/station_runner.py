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
from logging import StreamHandler

from rootio.config import DefaultConfig
from rootio.radio.models import Station
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..radio_station import RadioStation


class StationRunner:

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.__logger = self.__get_logger("service")
        self.run()

    def run(self):
        # set up scheduling
        lst_thr = threading.Thread(target=self.__start_listener, args=())
        lst_thr.start()

        try:
            engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI, pool_size=100)
            session = sessionmaker(bind=engine)()
            stations = session.query(Station).all()
        except Exception as e:
            self.__logger.error(e.message)
            return

        for station in stations:
            logger = self.__get_logger(station.id)
            radio_station = RadioStation(station, session, logger)
            logger.info('launching station : {0}'.format(station.id))
            t = threading.Thread(target=radio_station.run, args=())
            t.start()
        self.__logger.info(
            '================ Station runner service started at {0} =============='.format(datetime.utcnow()))

    def __get_logger(self, station_id):
        logger = logging.getLogger('station_runner_{0}'.format(station_id))
        log_folder = DefaultConfig.LOG_FOLDER
        file_hdlr = TimedRotatingFileHandler(os.path.join(log_folder, 'stations_{0}.log'.format(station_id)), when='midnight', interval=1)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_hdlr.setFormatter(formatter)

        logger.addHandler(file_hdlr)

        logger.setLevel(logging.DEBUG)
        return logger

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
                self.__logger.warning("Error on server bind, retrying. Retrying in 30 secs...")
                time.sleep(30)
        s.listen(0)
        self.__logger.info("Started TCP listener on port {0}".format(DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))

        while 1:
            cli, adr = s.accept()
            thrd = threading.Thread(target=self.__handle_tcp_connection, args=(cli,))
            thrd.daemon = True
            thrd.start()

    def __handle_tcp_connection(self, sck):  # TODO: handle json errors, else server will break due to rogue connection

        data = sck.recv(10240000)

        try:
            event = json.loads(data)
        except ValueError:
            total_data=[]
            total_data.append(data)
            while True:
                partial_data = sck.recv(10240000)
                if not partial_data: break
                total_data.append(partial_data)

            data = ''.join(total_data)
            try:
                event = json.loads(data)
            except ValueError:
                self.__logger.error('JSON load error')
                return

        if "action" in event and "station" in event:
            if event["action"] == "register":  # A station is registering
                self.__station_sockets[event["station"]] = sck
                self.__logger.info("Station {0} has registered for schedule change events".format(event["station"]))
            elif event["action"] in ["add", "delete", "update", "sync"] and "id" in event:  # Schedule is alerting of a change
                if event["station"] in self.__station_sockets:
                    try:
                        self.__station_sockets[event["station"]].send(data)
                        self.__logger.info("Event of type {0} sent to station {1} on scheduled program {2}"
                                         .format(event["action"], event["station"], event["id"]))
                        response = self.__station_sockets[event["station"]].recv(1024)
                        sck.send(response)
                    except Exception as e:
                        self.__logger.error("Event of type {0} failed for station {1} on scheduled program {2}"
                                         .format(event["action"], event["station"], event["id"]))
                        self.__logger.error("Event scheduler error: {0}".format(e))
                        self.__logger.error("Broken socket: {0}".format(self.__station_sockets[event['station']]))


if __name__ == "__main__":
    station_daemon = StationRunner()

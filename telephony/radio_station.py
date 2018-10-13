import time

from rootio.radio.models import Station

from call_handler import CallHandler
from program_handler import ProgramHandler
from community_menu import CommunityMenu


class RadioStation:

    def run(self):
        self.__program_handler.run()
        while True:
            time.sleep(1)
        return

    def stop(self):
        self.call_handler.stop()
        self.__program_handler.stop()
        pass

    def __init__(self, station, db, logger):
        self.logger = logger
        self.db = db
        self.station = station
        self.__program_handler = ProgramHandler(self)
        self.call_handler = CallHandler(self)
        self.__community_handler = CommunityMenu(self)
        self.logger.info("Starting up station {0}".format(self.station.name))
        return

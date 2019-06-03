import time

from rootio.radio.models import Station

from call_handler import CallHandler
from program_handler import ProgramHandler
from community_menu import CommunityIVRMenu


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
        self.id = station.id
        self.__program_handler = ProgramHandler(self)
        self.call_handler = CallHandler(self)
        community_menu_gw = self.__get_gateway_used()
        if community_menu_gw is not None:
            self.call_handler.register_community_ivr_number(str(community_menu_gw)[-9:])
        #self.__community_handler = CommunityIVRMenu(self)

        self.logger.info("Starting up station {0}".format(self.station.name))
        return

    # def __start_listener(self):
    #     self.__gateway = str(self.__get_gateway_used())[-9:]
    #     if self.__gateway is not None:
    #         self.__radio_station.call_handler.register_for_incoming_calls(self, True)
    #         self.__radio_station.call_handler.register_for_call_hangup(self, str(self.__gateway))
    #         # self.__radio_station.call_handler.register_for_media_playback_stop(self, str(self.__gateway))
    #         # self.__radio_station.call_handler.register_for_media_playback_start(self, str(self.__gateway))

    def __get_gateway_used(self):  # this retrieves the extension that listens for calls for ads and announcements
        try:
            gws = []
            for gw in self.station.incoming_gateways:
                gws.append(gw.number_bottom)
            gws.sort()

            if len(gws) > 0:
                return gws[0]
            else:
                return None
        except:
            return None

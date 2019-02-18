import datetime

from rootio.config import *
from rootio.content.models import CommunityContent
import json


class CommunityAction:

    def __init__(self, type_code, start_time, duration, program):
        self.__type_code = type_code
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__media_expected_to_stop = False
        self.__media_index = 0
        self.__call_handler = self.program.radio_station.call_handler
        self.__call_answer_info = None
        self.program.log_program_activity("Done initialising Media action for program {0}".format(self.program.name))

    def start(self):
        try:
            print "requesting call"
            self.__load_track()
            if self.__content is None or len(self.__content) < 1:  # If no content, do not even call
                print "No content"
                self.stop(True)
                return
            call_result = self.__request_station_call()
            print call_result
            if not call_result:  # !!
                print "call_result is not true!!"
                self.stop(False)
        except Exception as e:
            print e

    def stop(self, graceful=True, call_info=None):
        self.__media_expected_to_stop = True
        self.__stop_media(call_info)
        self.program.notify_program_action_stopped(graceful, call_info)

    def notify_call_answered(self, answer_info):
        self.program.log_program_activity(
            "Received call answer notification for Media action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-12:])
        self.__play_media(self.__call_answer_info, self.__media_index)
        self.__listen_for_media_play_stop()

    def __load_track(self):  # load the media to be played
        self.__content = self.program.radio_station.db.query(CommunityContent).filter(
            CommunityContent.type_code == self.__type_code).filter(
            CommunityContent.station_id == self.program.radio_station.station.id).filter(CommunityContent.valid_until >= datetime.datetime.now()).all()
        
    def __request_station_call(self):  # call the number specified thru plivo
        if self.program.radio_station.station.is_high_bandwidth:
            result = self.__call_station_via_sip()
            if result is None or not result[0]:  # Now try calling the SIM (ideally do primary, then secondary)
                result = self.__call_station_via_goip()
        else:
            result = self.__call_station_via_goip()
        return result

    def __call_station_via_sip(self):
        result = None
        # Try a high bandwidth call first
        if self.program.radio_station.station.sip_username is not None:
            result = self.__call_handler.call(self, self.program.radio_station.station.sip_username, self.program.name, True,
                                              self.duration)
            self.program.log_program_activity("result of station call via SIP is " + str(result))
        return result

    def __call_station_via_goip(self):
        result = None
        if self.program.radio_station.station.primary_transmitter_phone is not None:
            result = self.__call_handler.call(self, self.program.radio_station.station.primary_transmitter_phone.raw_number,
                                              self.program.name, False, self.duration)
            self.program.log_program_activity("result of station call (primary) via GoIP is " + str(result))
            if not result[0] and self.program.radio_station.station.secondary_transmitter_phone is not None:  # Go for the secondary line of the station, if duo SIM phone
                result = self.__call_handler.call(self,
                                              self.program.radio_station.station.secondary_transmitter_phone.raw_number,
                                                  self.program.name, False, self.duration)
                self.program.log_program_activity("result of station call (secondary) via GoIP is " + str(result))
        return result

    def __play_media(self, call_info, idx):  # play the media in the array
        self.program.log_program_activity("Playing media {0}".format(self.__content[idx].message))
        result = self.__call_handler.play(call_info['Channel-Call-UUID'],
                                          os.path.join(DefaultConfig.CONTENT_DIR, "community-content",
                                                       str(self.program.radio_station.station.id),
                                                       str(self.__type_code), self.__content[idx].message))
        self.program.log_program_activity('result of play is ' + result)
        if result.split(" ")[0] != "+OK":
            self.stop(False, call_info)

    def __stop_media(self, event_json):  # stop the media being played by the player
        try:
            self.program.log_program_activity(
                "Deregistered, all good, about to order hangup for {0}".format(self.program.name))
            self.__call_handler.deregister_for_call_hangup(event_json['Caller-Destination-Number'][-12:])
            self.__call_handler.deregister_for_media_playback_stop(event_json['Caller-Destination-Number'][-12:])
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'],
                                                   self.__content[self.__media_index])
            self.program.log_program_activity('result of stop play is ' + result)
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return

    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        self.stop(False, event_json)

    def notify_media_play_stop(self, event_json):
        if event_json["Media-Bug-Target"] == os.path.join(DefaultConfig.CONTENT_DIR, "community-content",
                                                          str(self.program.radio_station.station.id),
                                                          str(self.__type_code), self.__content[
                                                              self.__media_index % len(
                                                                  self.__content)].message):  # its our media
            # stopping, not some other media
            if self.__media_index >= len(self.__content) * 3:  # all media has played
                self.program.radio_station.logger.info(
                    "Played all media thrice in Interlude action for {0}, hanging up".format(self.program.name))
                self.stop(True, event_json)
            elif not self.__media_expected_to_stop:
                self.__media_index = self.__media_index + 1
                self.__play_media(self.__call_answer_info, self.__media_index % len(self.__content))

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self, self.__call_answer_info['Caller-Destination-Number'][-12:])

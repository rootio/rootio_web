from rootio.config import *
from rootio.content.models import ContentUploads, ContentTrack
from rootio.radio.models import ScheduledProgram


class MediaAction:

    def __init__(self, track_id, start_time, duration, program):
        self.__track_id = track_id
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__media = None
        self.__media_expected_to_stop = False
        self.__call_answer_info = None
        self.__call_handler = self.program.radio_station.call_handler
        self.program.log_program_activity("Done initing Media action for program {0}".format(self.program.name))
        self.__continuous_play = self.program.radio_station.db.query(ContentTrack).filter(ContentTrack.id == self.__track_id).first().continuous_play
        self.__continuous_play_limit = 1
        self.__play_counter = 1
        self.__episode_number = self.__get_episode_number(self.program.scheduled_program.program.id)

    def start(self):
        self.program.set_running_action(self)
        try:
            episode_number = self.__episode_number
            self.__media = self.__load_media(episode_number)
            if self.__media is not None:
                self.program.log_program_activity("Loaded playable media")
                call_result = self.__request_station_call()
                if not call_result[0]:  # !!
                    self.stop(False)
            else:
                self.program.log_program_activity("No playable media found, stopping this action...")
                self.stop(False)
        except Exception as e:
            self.program.radio_station.logger.error("error {err} in media_action.__start".format(err=str(e)))
            self.stop(False)


    def pause(self):
        self.__pause_media()

    def stop(self, graceful=True, call_info=None):
        if call_info is not None and not graceful:
            self.__stop_media(call_info)
        elif self.__call_answer_info is not None and not graceful:
            self.__stop_media(self.__call_answer_info)
        self.__stop_media(self.__call_answer_info)
        self.__deregister_listeners()
        self.program.notify_program_action_stopped(graceful, self.__call_answer_info)

    def notify_call_answered(self, answer_info):
        self.program.log_program_activity("Received call answer notification for Media action of {0} program"
                                          .format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-11:])
        self.__play_media(self.__call_answer_info)

    def __load_media(self, episode_number):  # load the media to be played
        episode_count = self.program.radio_station.db.query(ContentUploads).filter(ContentUploads.track_id == self.__track_id).count()
        self.__continuous_play_limit = episode_count
        if episode_count == 0:
            return None
        if episode_number > episode_count:
            index = (episode_number % episode_count) + 1
        else:
            index = episode_number

        if self.__continuous_play:
            index = self.__play_counter

        media = self.program.radio_station.db.query(ContentUploads)\
                                             .filter(ContentUploads.track_id == self.__track_id)\
                                             .filter(ContentUploads.order == index)\
                                             .first()

        #media.uri = os.path.join(DefaultConfig.CONTENT_DIR, media.uri)

        if media.deleted:
            self.__episode_number = self.__episode_number + 1
            if self.__play_counter <= episode_count:
                self.__play_counter = self.__play_counter + 1
                return self.__load_media(self.__episode_number)
            else:
                self.program.log_program_activity("No media found, aborting playback.")
                self.stop(False)
        else:
            return media

    def __get_episode_number(self, program_id):
        # Fix this below - Make RadioProgram inherit scheduled_program, rename it
        count = self.program.radio_station.db.query(ScheduledProgram)\
                                             .filter(ScheduledProgram.status == True)\
                                             .filter(ScheduledProgram.program_id == program_id)\
                                             .count()
        return count + 1

    def __request_station_call(self):  # call the number specified thru plivo
        # Check if the call exists, start with the least likely number to be called
        if self.program.radio_station.station.secondary_transmitter_phone is not None and self.__call_handler.call_exists(self.program.radio_station.station.secondary_transmitter_phone.raw_number):
            result = self.__call_handler.call(self,
                                              self.program.radio_station.station.secondary_transmitter_phone.raw_number,
                                              self.program.name, False, self.duration)
            return result
        elif self.program.radio_station.station.primary_transmitter_phone is not None and self.__call_handler.call_exists(self.program.radio_station.station.primary_transmitter_phone.raw_number):
            result = self.__call_handler.call(self,
                                              self.program.radio_station.station.primary_transmitter_phone.raw_number,
                                              self.program.name, False, self.duration)
            return result
        elif self.program.radio_station.station.sip_username is not None and self.__call_handler.call_exists(self.program.radio_station.station.sip_username):
            result = self.__call_handler.call(self, self.program.radio_station.station.sip_username, self.program.name,
                                              True, self.duration)
            self.program.log_program_activity("result of station call via SIP is " + str(result))
            return result

        # At this point we are sure that no call to the station exists. We will try to initiate a new call
        if self.program.radio_station.station.is_high_bandwidth:
            result = self.__call_station_via_sip()
            if result is None or not result[0]:  # Now try calling the SIM (ideally do primary, then secondary)
                result = self.__call_station_via_goip()
        else:
            result = self.__call_station_via_goip()
        return result

    def __call_station_via_sip(self):
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
                                              self.program.name, False,
                                          self.duration)
            self.program.log_program_activity("result of station call (primary) via GoIP is " + str(result))
            if not result[0] and self.program.radio_station.station.secondary_transmitter_phone is not None:  # Go for the secondary line of the station, if duo SIM phone
                result = self.__call_handler.call(self,
                                              self.program.radio_station.station.secondary_transmitter_phone.raw_number,
                                                  self.program.name, False,
                                              self.duration)
                self.program.log_program_activity("result of station call (secondary) via GoIP is " + str(result))
        return result

    def __play_media(self, call_info):  # play the media in the array

        self.program.log_program_activity("Playing media {0}".format(self.__media.name))
        self.__listen_for_media_play_stop()
        result = self.__call_handler.play(call_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR, self.__media.uri))
        self.program.log_program_activity('result of play is ' + result)
        if result.split(" ")[0] != "+OK":
            self.stop(False, call_info)

    def __pause_media(self):  # pause the media in the array
        pass

    def __stop_media(self, event_json):  # stop the media being played by the player
        try:
            self.program.log_program_activity("Deregistered, all good, about to order hangup for {0}"
                                              .format(self.program.name))
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR, self.__media.uri))
            self.program.log_program_activity('result of stop play is ' + result)
        except Exception as e:
            self.program.radio_station.logger.error("error {err} in media_action.__stop_media".format(err=e.message))
            return

    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        #self.stop(False)
        self.__request_station_call()

    def notify_media_play_stop(self, event_json):
        #  if event_json["Media-Bug-Target"] == os.path.join(DefaultConfig.CONTENT_DIR, media.uri) and self.__is_valid:
        try:
            if self.__is_valid:
                if self.__continuous_play:
                    self.program.log_program_activity(
                        'continuous play is on, will move on to the rest of the episodes ({})'.format(
                            self.__continuous_play_limit))
                    if self.__play_counter < self.__continuous_play_limit:
                        self.__play_counter = self.__play_counter + 1
                        self.__episode_number = self.__play_counter
                        self.program.log_program_activity('will now play episode #{}'.format(self.__play_counter))
                        self.start()
                    else:
                        self.program.log_program_activity("No more files to play. Should proceed to hangup")
                        self.stop(True, event_json)
                        self.__is_valid = False
                else:
                    self.program.log_program_activity("Continuous play is not enabled. Should proceed to next track/hangup")
                    self.stop(True, event_json)
                    self.__is_valid = False
        except Exception as e:
            self.program.radio_station.logger.error("error {err} in media_action.notify_media_play_stop".format(err=e.message))
            self.stop(False, event_json)

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self, self.__call_answer_info['Caller-Destination-Number'][-11:])

    def __deregister_listeners(self):
        if self.__call_answer_info is not None:
            self.__call_handler.deregister_for_media_playback_stop(self.__call_answer_info['Caller-Destination-Number'][-11:])
            self.__call_handler.deregister_for_call_hangup(self.__call_answer_info['Caller-Destination-Number'][-11:])
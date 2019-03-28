import json
import threading
from datetime import datetime

from freeswitchESL.ESL import *
from sqlalchemy.exc import SQLAlchemyError

from cereproc.cereproc_rest_agent import CereprocRestAgent
from rootio.config import DefaultConfig
from rootio.telephony.models import Gateway, Call


class CallHandler:

    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__incoming_call_recipients = dict()
        self.__incoming_dtmf_recipients = dict()
        self.__outgoing_call_recipients = dict()
        self.__host_call_recipients = dict()
        self.__waiting_call_recipients = dict()
        self.__call_hangup_recipients = dict()
        self.__available_calls = dict()
        self.__media_playback_stop_recipients = dict()
        self.__media_playback_start_recipients = dict()
        self.__speech_start_recipients = dict()
        self.__speech_stop_recipients = dict()

        # get the gateways to be used for telephony
        self.__load_incoming_gateways()
        self.__load_outgoing_gateways()

        # start listener for ESL events
        self.__start_esl_listener()

        # configure cereproc agent
        self._cprc_agent = CereprocRestAgent(DefaultConfig.CEREPROC_SERVER, DefaultConfig.CEREPROC_USERNAME,
                                             DefaultConfig.CEREPROC_PASSWORD)  # ToDo: defaults to English,
        #  male, 1600, wav. Pick args from station attributes.

    def __start_esl_listener(self):
        t = threading.Thread(target=self.__listen_for_esl_events, args=())
        t.daemon = True
        t.start()

    def __connect_esl(self):
        esl_server = DefaultConfig.ESL_SERVER
        esl_port = DefaultConfig.ESL_PORT
        esl_authentication = DefaultConfig.ESL_AUTHENTICATION
        return ESLconnection(esl_server, esl_port, esl_authentication)

    def __load_incoming_gateways(self):
        gws = self.__radio_station.db.query(Gateway).join(Gateway.stations_using_for_incoming).filter_by(
            id=self.__radio_station.station.id).all()
        self.__incoming_gateways = dict()
        self.__available_incoming_gateways = []
        for gw in gws:
            self.__incoming_gateways[str(gw.number_bottom)] = gw
            self.__available_incoming_gateways.append(gw.number_bottom)
            self.__available_incoming_gateways.sort()
            self.__radio_station.logger.info(
                "Got incoming gateways for {0} {1}".format(self.__radio_station.station.name,
                                                           str(self.__available_incoming_gateways)))

    def __load_outgoing_gateways(self):
        gws = self.__radio_station.db.query(Gateway).join(Gateway.stations_using_for_outgoing).filter_by(
            id=self.__radio_station.station.id).all()
        self.__outgoing_gateways = dict()
        self.__outgoing_sip_gateways = dict()
        self.__available_outgoing_gateways = []
        for gw in gws:
            if gw.is_goip:
                self.__outgoing_gateways[str(gw.number_bottom)] = gw
                self.__available_outgoing_gateways.append(gw.number_bottom)
                self.__available_outgoing_gateways.sort()
                self.__radio_station.logger.info(
                    "Got outgoing goip gateways for {0} {1}".format(self.__radio_station.station.name,
                                                                    str(self.__available_outgoing_gateways)))
            else:  # really all you need is one outgoing :-)
                self.__outgoing_sip_gateways[str(gw.number_bottom)] = gw
                self.__radio_station.logger.info(
                    "Got outgoing SIP gateways for {0} {1}".format(self.__radio_station.station.name,
                                                                   str(self.__outgoing_sip_gateways)))

    def __do_esl_command(self, esl_command):
        self.__radio_station.logger.info("Executing ESL Command: {0}".format(esl_command))
        con = self.__connect_esl()
        result = con.api(esl_command)
        try:
            con.disconnect()
            return result.getBody()
        except Exception, e:
            self.__radio_station.logger.error(e.message)
            return None

    def register_for_call_hangup(self, recipient, to_number):
        self.__call_hangup_recipients[to_number] = recipient
        self.__radio_station.logger.info(
            "Added {0} to incoming call hangup recipients {1}".format(recipient, str(self.__call_hangup_recipients)))

    def register_for_host_call(self, recipient, host_number):
        self.__host_call_recipients[host_number] = recipient
        self.__radio_station.logger.info(
            "The program {0} is now listening for host calls from {1}".format(recipient, host_number))

    def register_for_incoming_calls(self, recipient, is_community_menu=False):
        gws = self.__incoming_gateways.keys()
        gws.sort()
        if is_community_menu:  # register only the first gateway, only 9 digits to match various incoming formats
            if len(gws) > 0:
                self.__incoming_call_recipients[gws[0][-9:]] = recipient
        else:
            for x in range(1, len(gws)):  # skip the first, used by community menu
                self.__incoming_call_recipients[gws[x][-9:]] = recipient
                self.__radio_station.logger.info(
                    "Added {0} to incoming call recipients {1}".format(recipient, str(self.__incoming_call_recipients)))

    def register_for_incoming_dtmf(self, recipient, from_number):
        self.__incoming_dtmf_recipients[from_number] = recipient
        self.__radio_station.logger.info(
            "Added {0} to incoming dtmf recipients {1}".format(recipient, str(self.__incoming_dtmf_recipients)))

    def deregister_for_incoming_dtmf(self, from_number):
        if from_number in self.__incoming_dtmf_recipients:
            del self.__incoming_dtmf_recipients[from_number]

    def register_for_speak_start(self, recipient, from_number):
        self.__speech_start_recipients[from_number] = recipient
        self.__radio_station.logger.info(
            "Added {0} to speak start recipients {1}".format(recipient, str(self.__speech_start_recipients)))

    def deregister_for_speak_start(self, from_number):
        if from_number in self.__speech_start_recipients:
            del self.__speech_start_recipients[from_number]

    def register_for_speak_stop(self, recipient, from_number):
        self.__speech_stop_recipients[from_number] = recipient
        self.__radio_station.logger.info(
            "Added {0} to speak stop recipients {1}".format(recipient, str(self.__speech_stop_recipients)))

    def deregister_for_speak_stop(self, from_number):
        if from_number in self.__speech_stop_recipients:
            del self.__speech_stop_recipients[from_number]

    def register_for_media_playback_stop(self, recipient, from_number):
        self.__media_playback_stop_recipients[from_number] = recipient
        self.__radio_station.logger.info("Added {0} to media playback stop recipients {1}".format(recipient, str(
            self.__media_playback_stop_recipients)))

    def register_for_media_playback_start(self, recipient, from_number):
        self.__media_playback_start_recipients[from_number] = recipient
        self.__radio_station.logger.info("Added {0} to media playback start recipients {1}".format(recipient, str(
            self.__media_playback_start_recipients)))

    def deregister_for_incoming_calls(self, recipient):
        self.__incoming_call_recipients = dict()
        self.__radio_station.logger.info(
            "Removed {0} from call hangup recipients {1}".format(recipient, str(self.__incoming_call_recipients)))

    def deregister_for_call_hangup(self, from_number):
        if from_number in self.__call_hangup_recipients:
            del self.__call_hangup_recipients[from_number]
            self.__radio_station.logger.info(
                "Removed {0} from call hangup recipients {1}".format(from_number, str(self.__call_hangup_recipients)))

    def deregister_for_media_playback_stop(self, from_number):
        if from_number in self.__media_playback_stop_recipients:
            del self.__media_playback_stop_recipients[from_number]
            self.__radio_station.logger.info("Removed {0} from media playback stop recipients {1}"
                                             .format(from_number, str(self.__media_playback_stop_recipients)))

    def deregister_for_media_playback_start(self, from_number):
        if from_number in self.__media_playback_start_recipients:
            del self.__media_playback_start_recipients[from_number]
            self.__radio_station.logger.info("Removed {0} from media playback start recipients {1}"
                                             .format(from_number, str(self.__media_playback_start_recipients)))

    def call(self, program_action, to_number, argument, use_sip=False,
             time_limit=0):  # redundant params will be used later
        if to_number in self.__available_calls.keys():
            self.__radio_station.logger.info(
                "Existing call to {0} requested for action on argument '{1}, being returned".format(to_number,
                                                                                                    argument))
            program_action.notify_call_answered(self.__available_calls[to_number])
            return True, self.__available_calls[to_number]['Channel-Call-UUID']
        else:
            if self.__radio_station.station.is_high_bandwidth and use_sip and len(self.__outgoing_sip_gateways) > 0:
                self.__radio_station.logger.info(
                    "SIP GWS before pop are {0}".format(str(self.__outgoing_sip_gateways)))
                gw = self.__outgoing_sip_gateways.values()[0]
                self.__radio_station.logger.info(
                    "SIP GWS after pop are {0}".format(str(self.__outgoing_sip_gateways)))
                if gw.gateway_prefix is None:
                    gw.gateway_prefix = ''
                call_command = 'originate {{{0}}}{1}/{2}{3} &conference("{4}_{5}")'.format(gw.extra_string,
                                                                                           gw.sofia_string,
                                                                                           gw.gateway_prefix, to_number,
                                                                                           program_action.program.id,
                                                                                           program_action.program
                                                                                           .radio_station.station.id)
                self.__radio_station.logger.info(
                    "setting up new call for argument '{0}': {1}".format(argument, call_command))
                self.__waiting_call_recipients[str(to_number)[-9:]] = program_action
                result = self.__do_esl_command(call_command)
                self.__radio_station.logger.info("Result of call ESL command is {0}".format(result))
                self.__radio_station.logger.info(
                    "SIP GWS after call are {0}".format(str(self.__outgoing_sip_gateways)))
                if result is not None and result.split(" ")[0] == "+OK":
                    return True, result.split(" ")[1]
                else:
                    return False, None
            else:
                self.__radio_station.logger.info(
                    "GWS before pop are {0}".format(str(self.__available_outgoing_gateways)))
                gw = self.__outgoing_gateways[str(self.__available_outgoing_gateways.pop())[-12:]]
                self.__radio_station.logger.info(
                    "GWS after pop are {0}".format(str(self.__available_outgoing_gateways)))
                if gw.gateway_prefix is None:
                    gw.gateway_prefix = ''
                call_command = 'originate {{{0}}}{1}/{2}{3} &conference("{4}_{5}")'.format(gw.extra_string,
                                                                                           gw.sofia_string,
                                                                                           gw.gateway_prefix, to_number,
                                                                                           program_action.program.id,
                                                                                           program_action.program
                                                                                           .radio_station.station.id)
                self.__radio_station.logger.info(
                    "setting up new call for argument '{0}': {1}".format(argument, call_command))
                self.__waiting_call_recipients[str(to_number)[-12:]] = program_action
                result = self.__do_esl_command(call_command)
                self.__radio_station.logger.info("Result of call ESL command is {0}".format(result))
                if result is None or result.split(" ")[0] != "+OK":
                    self.__available_outgoing_gateways.append(gw.number_bottom)
                    self.__available_outgoing_gateways.sort()
                self.__radio_station.logger.info(
                    "GWS after call are {0}".format(str(self.__available_outgoing_gateways)))
                if result is not None and result.split(" ")[0] == "+OK":
                    return True, result.split(" ")[1]
                else:
                    return False, None

    def bridge_incoming_call(self, call_uuid, call_id):
        bridge_command = 'uuid_transfer {0} conference:"{1}"@default inline'.format(call_uuid, call_id)
        self.__radio_station.logger.info("Bridging call from {0} into conference {1}".format(call_uuid, call_id))
        return self.__do_esl_command(bridge_command)

    def schedule_hangup(self, seconds, call_uuid):
        hangup_command = 'sched_hangup +{} {}'.format(seconds, call_uuid)
        self.__radio_station.logger.info(
            "setting up hangup for {0} seconds into call with UUID {1}".format(seconds, call_uuid))
        return self.__do_esl_command(hangup_command)

    def hangup(self, call_uuid):
        self.__radio_station.logger.info("preparing hangup for call with UUID {0}".format(call_uuid))
        hangup_command = 'uuid_kill {}'.format(call_uuid)
        self.__radio_station.logger.info("ordering hangup for call with UUID {0}".format(call_uuid))
        self.__do_esl_command(hangup_command)  # possibly segfaults

    def play(self, call_uuid, file_location):
        play_command = "uuid_displace {0} start \'{1}\'".format(call_uuid, file_location.replace('\'',
                                                                                                 '\\\''))  # single quote breaks FS
        self.__radio_station.logger.info("Playing file {0} into call with UUID {1}".format(file_location, call_uuid))
        return self.__do_esl_command(play_command)

    def stop_play(self, call_uuid, content_location):
        stop_play_command = 'uuid_displace {0} stop \'{1}\''.format(call_uuid, content_location)
        return self.__do_esl_command(stop_play_command)

    def speak(self, phrase, call_uuid):
        try:
            (tts_file, metadata) = self._cprc_agent.get_cprc_tts(phrase)
            return self.play(call_uuid, tts_file)
        except Exception as e:
            self.__radio_station.logger.info("Error with TTS generation: {0}".format(e))
            return None

    def __listen_for_esl_events(self):
        esl_connection = self.__connect_esl()
        events_to_catch = ["CHANNEL_ANSWER", "DTMF", "DETECTED_SPEECH", "NOTALK", "CHANNEL_HANGUP", "CHANNEL_PARK",
                           "MEDIA_BUG_START", "MEDIA_BUG_STOP"]
        for event in events_to_catch:
            esl_connection.events("plain", event)

        while 1:
            e = esl_connection.recvEvent()
            if not e:
                return

            try:
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
            except ValueError as e:
                continue  # rogue value. move on..

            event_name = e.getHeader("Event-Name")

            # print event_name
            if event_name == "CHANNEL_ANSWER" and 'Caller-Destination-Number' in event_json:
                try:
                    self.__radio_station.logger.info("received answer for {0} with waiting recipients {1}".format(
                        event_json['Caller-Destination-Number'], self.__waiting_call_recipients.keys()))
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__waiting_call_recipients:
                        self.__available_calls[str(event_json['Caller-Destination-Number'])[-12:]] = event_json
                        self.__waiting_call_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_call_answered(event_json)
                        self.__radio_station.logger.info(
                            "Deleting recipient {0} from waiting call recipients {1}".format(
                                str(event_json['Caller-Destination-Number'])[-12:], self.__waiting_call_recipients))
                        del self.__waiting_call_recipients[str(event_json['Caller-Destination-Number'])[-12:]]
                    elif str(event_json['Caller-Destination-Number'])[-9:] in self.__waiting_call_recipients:
                        self.__available_calls[str(event_json['Caller-Destination-Number'])[-9:]] = event_json
                        self.__waiting_call_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_call_answered(event_json)
                        self.__radio_station.logger.info(
                            "Deleting recipient {0} from waiting call recipients {1}".format(
                                str(event_json['Caller-Destination-Number'])[-9:], self.__waiting_call_recipients))
                        del self.__waiting_call_recipients[str(event_json['Caller-Destination-Number'])[-9:]]
                except e:
                    self.__radio_station.logger.error('error in channel answer: {0}'.format(e.message))

            elif event_name == "DTMF" and 'Caller-Destination-Number' in event_json:
                try:
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__incoming_dtmf_recipients:
                        self.__radio_station.logger.info(
                            "Received DTMF [{0}] for recipient {1} in {2}".format(event_json["DTMF-Digit"],
                                                                                  event_json[
                                                                                      'Caller-Destination-Number'],
                                                                                  self.__incoming_dtmf_recipients))
                        threading.Thread(target=self.__incoming_dtmf_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_incoming_dtmf,
                                         args=(event_json,)).start()
                    elif str(event_json['Caller-Destination-Number'])[-9:] in self.__incoming_dtmf_recipients:
                        self.__radio_station.logger.info(
                            "Received DTMF [{0}] for recipient {1} in {2}".format(event_json["DTMF-Digit"],
                                                                                  event_json[
                                                                                      'Caller-Destination-Number'],
                                                                                  self.__incoming_dtmf_recipients))
                        threading.Thread(target=self.__incoming_dtmf_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_incoming_dtmf,
                                         args=(event_json,)).start()
                except e:
                    self.__radio_station.logger.error('error in DTMF detection: {0}'.format(e.message))

            elif event_name == "DETECTED_SPEECH" and 'Caller-Destination-Number' in event_json:
                try:
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__speech_start_recipients:
                        self.__radio_station.logger.info(
                            "Speech on call to [{0}] ".format(event_json['Caller-Destination-Number']))
                        threading.Thread(target=self.__speech_start_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_speech_start,
                                         args=(event_json,)).start()
                except e:
                    self.__radio_station.logger.error('error in speak start: {0}'.format(e.message))

            elif event_name == "NOTALK" and 'Caller-Destination-Number' in event_json:
                try:
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__speech_stop_recipients:
                        self.__radio_station.logger.info(
                            "Speech stopped on call to [{0}] ".format(event_json['Caller-Destination-Number']))
                        threading.Thread(target=self.__speech_stop_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_speech_stop,
                                         args=(event_json,)).start()
                except e:
                    self.__radio_station.logger.error('error in speak end: {0}'.format(e.message))

            elif event_name == "CHANNEL_HANGUP" and 'Caller-Destination-Number' in event_json:
                try:
                    loggable = False
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__call_hangup_recipients:
                        self.__call_hangup_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_call_hangup(event_json)
                        loggable = True
                    elif str(event_json['Caller-Destination-Number'])[-9:] in self.__call_hangup_recipients:
                        self.__call_hangup_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_call_hangup(event_json)
                        loggable = True
                    # remove the call from the list of available calls
                    if str(event_json['Caller-Destination-Number'])[-12:] in self.__available_calls:
                        self.__radio_station.logger.info("Removing call to {0} from available calls {1}".format(
                            str(event_json['Caller-Destination-Number'])[-12:], self.__available_calls.keys()))
                        del self.__available_calls[str(event_json['Caller-Destination-Number'])[-12:]]
                        self.__release_gateway(event_json)
                        loggable = True
                    elif str(event_json['Caller-Destination-Number'])[-9:] in self.__available_calls:
                        self.__radio_station.logger.info("Removing call to {0} from available calls {1}".format(
                            str(event_json['Caller-Destination-Number'])[-9:], self.__available_calls.keys()))
                        del self.__available_calls[str(event_json['Caller-Destination-Number'])[-9:]]
                        self.__release_gateway(event_json)
                        loggable = True

                    # log the call
                    if loggable:
                        self.__log_call(event_json)

                    if event_json['Caller-Destination-Number'] in self.__media_playback_stop_recipients:
                        del self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']]
                except e:
                    self.__radio_station.logger.error('error in channel hangup: {0}'.format(e.message))

            # This should use 9 digits not 12!
            elif event_name == "CHANNEL_PARK" and 'Caller-Destination-Number' in event_json:
                try:
                    self.__radio_station.logger.info("Notifying park recipient for {0} in {1} and {2}".format(
                        event_json['Caller-Destination-Number'][-9:], self.__incoming_call_recipients,
                        self.__host_call_recipients))
                    if event_json['Caller-Destination-Number'][
                       -9:] in self.__incoming_call_recipients:  # Someone calling into a talk show
                        threading.Thread(target=self.__incoming_call_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_incoming_call,
                                         args=(event_json,)).start()
                    elif event_json['Caller-ANI'][-9:] in self.__host_call_recipients:
                        self.__host_call_recipients[event_json['Caller-ANI'][-9:]].notify_host_call(event_json)
                    elif event_json['Caller-Destination-Number'][
                       -12:] in self.__incoming_call_recipients:  # Someone calling into a talk show
                        threading.Thread(target=self.__incoming_call_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_incoming_call,
                                         args=(event_json,)).start()
                    elif event_json['Caller-ANI'][-12:] in self.__host_call_recipients:
                        self.__host_call_recipients[event_json['Caller-ANI'][-12:]].notify_host_call(event_json)
                except e:
                    self.__radio_station.logger.error('error in channel park: {0}'.format(e.message))

            elif event_name == "MEDIA_BUG_START" and 'Caller-Destination-Number' in event_json:
                try:
                    if event_json['Caller-Destination-Number'][-12:] in self.__media_playback_start_recipients:
                        self.__radio_station.logger.info(
                            "Notifying media playback start recipient for {0} in {1}".format(
                                event_json['Caller-Destination-Number'], self.__media_playback_start_recipients))
                        threading.Thread(target=self.__media_playback_start_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_media_play_start,
                                         args=(event_json,)).start()
                        # del self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']]
                    elif event_json['Caller-Destination-Number'][-9:] in self.__media_playback_start_recipients:
                        self.__radio_station.logger.info(
                            "Notifying media playback start recipient for {0} in {1}".format(
                                event_json['Caller-Destination-Number'], self.__media_playback_start_recipients))
                        threading.Thread(target=self.__media_playback_start_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_media_play_start,
                                         args=(event_json,)).start()
                        # del self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']]
                except e:
                    self.__radio_station.logger.error('error in media bug stop: {0}'.format(e.message))

            elif event_name == "MEDIA_BUG_STOP" and 'Caller-Destination-Number' in event_json:
                try:
                    if event_json['Caller-Destination-Number'][-12:] in self.__media_playback_stop_recipients:
                        # self.__radio_station.logger.info("got media stop bug as {0}".format(event_json_string))
                        self.__radio_station.logger.info(
                            "Notifying media playback stop recipient for {0} in {1}".format(
                                event_json['Caller-Destination-Number'], self.__media_playback_stop_recipients))
                        threading.Thread(target=self.__media_playback_stop_recipients[
                            str(event_json['Caller-Destination-Number'])[-12:]].notify_media_play_stop,
                                         args=(event_json,)).start()
                        # del self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']]
                    elif event_json['Caller-Destination-Number'][-9:] in self.__media_playback_stop_recipients:
                        # self.__radio_station.logger.info("got media stop bug as {0}".format(event_json_string))
                        self.__radio_station.logger.info(
                            "Notifying media playback stop recipient for {0} in {1}".format(
                                event_json['Caller-Destination-Number'], self.__media_playback_stop_recipients))
                        threading.Thread(target=self.__media_playback_stop_recipients[
                            str(event_json['Caller-Destination-Number'])[-9:]].notify_media_play_stop,
                                         args=(event_json,)).start()
                        # del self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']]
                except e:
                    self.__radio_station.logger.error('error in media bug stop: {0}'.format(e.message))

    def record_call(self, call_uuid, path):
        record_command = "uuid_record {0} start '{1}'".format(call_uuid, path)
        self.__radio_station.logger.info("setting up recording for call with UUID {0}".format(call_uuid))
        return self.__do_esl_command(record_command)

    def stop_record_call(self, call_uuid, path):
        stop_record_command = "uuid_record {0} stop '{1}'".format(call_uuid, path)
        return self.__do_esl_command(stop_record_command)

    def __log_call(self, event_json):
        try:
            call = Call()
            call.call_uuid = event_json['Channel-Call-UUID']
            call.start_time = datetime.fromtimestamp(float(event_json['Caller-Channel-Answered-Time'][0:-6]))
            call.duration = (
                    datetime.fromtimestamp(float(event_json['Event-Date-Timestamp'][0:-6])) - call.start_time).seconds
            call.from_phonenumber = event_json['Caller-ANI']
            call.to_phonenumber = event_json['Caller-Destination-Number']
            call.station_id = self.__radio_station.station.id
        except KeyError as e:
            self.__radio_station.logger.error('error in __log_call: {0}'.format(e.message))
            return
        except:
            return

        try:
            self.__radio_station.db._model_changes = {}
            self.__radio_station.db.add(call)
            self.__radio_station.db.commit()
        except SQLAlchemyError as e:
            self.__radio_station.logger.error('error in logging call: {0}'.format(e.message))
            try:
                self.__radio_station.db.rollback()
            except:
                return

        except:  # any other exception. This loop should not stop for anything.
            return

    def __release_gateway(self, event_json):
        # if it was an incoming call
        if event_json['Caller-Destination-Number'][:-12] in self.__outgoing_gateways.keys():
            self.__radio_station.logger.info("Putting back gateway {0} to available gateways {1}".format(
                event_json['Caller-Destination-Number'][:-12], self.__outgoing_gateways))
            self.__available_outgoing_gateways.append(event_json['Caller-Destination-Number'])
        # if it is an outbound call
        if 'Caller-ANI' in event_json and event_json['Caller-ANI'][-12:] in self.__outgoing_gateways.keys():
            self.__radio_station.logger.info(
                "Putting back gateway {0} to available gateways {1}".format(event_json['Caller-ANI'][:-12],
                                                                            self.__outgoing_gateways))
            self.__available_outgoing_gateways.append(int(event_json['Caller-ANI'][-12:]))
        self.__available_outgoing_gateways.sort()


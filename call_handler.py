# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 2:15:22 PM$"

from ESL import *
from rootio.config import *
from rootio.telephony import *
from rootio.telephony.models import Gateway
import plivohelper
import threading
import json
import time
from sets import Set

#Define some constants - though these should come from the config
ESL_SERVER = '127.0.0.1'
ESL_PORT = 8021
ESL_AUTHENTICATION = 'ClueCon'


class CallHandler:
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        t = threading.Thread(target=self.__handle_dtmf, args=())
        t.daemon = True
        t.start()
        self.__incoming_call_recipients = dict()
        self.__incoming_dtmf_recipients = dict()
        self.__outgoing_call_recipients = dict()
        self.__waiting_call_recipients = dict()
        self.__available_calls = dict()
        self.__media_playback_stop_recipients = dict()
        self.__listen_for_hangup()
        #Create connection for DTMF 
        self.__listen_for_media_play_stop()
        self.__listen_for_incoming_calls()

        #get the gateways to be used for telephony
        self.__load_station_gateways()

    def __load_station_gateways(self):
        gws = self.__radio_station.db.session.query(Gateway).join(Gateway.stations_using_for_incoming).filter_by(id=self.__radio_station.id).all()
        self.__gateways = dict()
        self.__available_gateways = []
        for gw in gws:
            print gw.number_bottom
            self.__gateways[str(gw.number_bottom)] = gw
            self.__available_gateways.append(gw.number_bottom)
            self.__available_gateways.sort()
            #self.__available_gateways.reverse()
        print self.__gateways.keys()
    
    def __do_ESL_command(self, ESL_command):
        result = self.__ESLConnection.api(ESL_command)
        try:
            return result.getBody()
        except Exception, e:
            print str(e)
            return None

    def register_for_incoming_calls(self, recipient, to_number):
        self.__incoming_call_recipients[to_number] = recipient

    def register_for_incoming_dtmf(self, recipient, from_number):
        self.__incoming_dtmf_recipients[from_number] = recipient

    def register_for_media_playback_stop(self, recipient, from_number):
        self.__media_playback_stop_recipients[from_number] = recipient

    def deregister_for_media_playback_stop(self, recipient, from_number):
        del self.__media_playback_stop_recipients[from_number]

    def call(self, program_action, to_number, action, argument, time_limit):
        if to_number in self.__available_calls.keys():
            program_action.notify_call_answered(self.__available_calls[to_number])
        else:
            gw = self.__gateways[str(self.__available_gateways.pop())[-9:]]
            call_command = 'originate {{{0}}}{1}/{2}{3} &conference("{4}_{5}")'.format(gw.extra_string, gw.sofia_string, gw.gateway_prefix, to_number, program_action.program.id, program_action.program.radio_station.id)
            print call_command
            self.__waiting_call_recipients[to_number] = program_action
            t = threading.Thread(target=self.__report_answered, args=(program_action,))
            #t.daemon = True
            t.start()
            self.__do_ESL_command(call_command)

    def schedule_hangup(self, seconds, call_UUID):
        hangup_command = 'sched_hangup +{} {}'.format(seconds, call_UUID)
        return self.__do_ESL_command(hangup_command)
        
    def hangup(self, call_UUID):
        hangup_command = 'uuid_kill {}'.format(call_UUID)
        return self.__do_ESL_command(hangup_command)
           
    
    def play(self, file_location, call_UUID):
        play_command = 'uuid_displace {1} start \'{0}\''.format(call_UUID, file_location)
        return self.__do_ESL_command(play_command)
    
    def stop_play(self, call_UUID, content_location):
        stop_play_command = 'uuid_displace {0} stop \'{1}\''.format(call_UUID, content_location)
        return self.__do_ESL_command(stop_play_command)

    def speak(self, phrase, call_UUID):
        speak_command = 'speak stuff'
        return self.__do_ESL_command(speak_command) 
        
    
    def __report_answered(self, program_action):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_ANSWER")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                self.__available_calls[str(event_json['Caller-Destination-Number'])[-10:]] = event_json
                print "received answer for {0}".format(event_json['Caller-Destination-Number'])
                print self.__waiting_call_recipients.keys()
                self.__record_call(event_json['Channel-Call-UUID'], event_json['variable_sip_from_user'], event_json['Caller-Destination-Number'])
                if str(event_json['Caller-Destination-Number'])[-10:] in self.__waiting_call_recipients:
                    self.__waiting_call_recipients[str(event_json['Caller-Destination-Number'])[-10:]].notify_call_answered(event_json)            
                    del self.__waiting_call_recipients[str(event_json['Caller-Destination-Number'])[-10:]]
                    break

    def __record_call(self, call_UUID, from_number, destination_number):
        record_command = "uuid_record {0} start '/home/amour/test_media/RootioNew/Northern Uganda Pilot/Luo_Recordings/Call_Recordings/{1}_{2}_{3}_recording.wav'".format(call_UUID, from_number, destination_number, time.strftime("%Y_%m_%d_%H_%M_%S"))
        result = self.__do_ESL_command(record_command)

    def request_conference(self, call_UUID, conference_UUID):
        break_command = 'break {0}'.format(conference_UUID)#currently al calls are added to conf. is there need to have a call not in conf?
        return self.__do_ESL_command(break_command) 

    def __handle_dtmf(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "DTMF")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got DTMF event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                if 'Caller-Destination-Number' in event_json and event_json['Caller-Destination-Number'] in self.__incoming_dtmf_recipients:
                    self.__incoming_dtmf_recipients[event_json['Caller-Destination-Number']].notify_incoming_dtmf(event_json)
    
    def __listen_for_media_play_stop(self):
        t = threading.Thread(target=self.__handle_media_play_stop, args=())
        t.daemon = True
        t.start()
    
    def __listen_for_incoming_calls(self):
        t = threading.Thread(target=self.__handle_incoming_calls, args=())
        t.daemon = True
        t.start()

    def __listen_for_hangup(self):
        t = threading.Thread(target=self.__handle_hangup, args=())
        t.daemon = True
        t.start()

    def __handle_hangup(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_HANGUP")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got hangup event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                #remove the call from the list of available calls
                if 'Caller-Destination-Number' in event_json and str(event_json['Caller-Destination-Number'])[-10:] in self.__available_calls:
                    del self.__available_calls[str(event_json['Caller-Destination-Number'])[-10:]]
                self.__release_gateway(event_json)
 
    def __handle_incoming_calls(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_PARK")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got incoming call event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                self.__incoming_call_recipients[event_json['Caller-Destination-Number']].notify_incoming_call(event_json)
                del self.__incoming_call_recipients[event_json['Caller-Destination-Number']] 

    def __handle_media_play_stop(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "MEDIA_BUG_STOP")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got Media bug event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                try:
                    if  event_json['Caller-Destination-Number'] in  self.__media_playback_stop_recipients:
                        self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']].notify_media_play_stop(event_json)
                except e:
                    print str(e)
                   
    def __claim_gateway(self, event_json):
        pass
            #self.__available_gateways.discard(event_json['Caller-Caller-ID-Number'])

    def __release_gateway(self, event_json):
        #if it was an incoming call
        if 'Caller-Destination-Number' in event_json and event_json['Caller-Destination-Number'][:-9] in self.__gateways.keys():
            self.__available_gateways.append(event_json['Caller-Destination-Number'])
            print "putting back {0}".format(event_json['Caller-Destination-Number'])
        #if it is an outbound call
        if 'variable_sip_from_user' in event_json and event_json['variable_sip_from_user'][-9:] in self.__gateways.keys():
            self.__available_gateways.append(int(event_json['variable_sip_from_user'][-9:]))
            print "putting back {0}".format(event_json['variable_sip_from_user'])
        self.__available_gateways.sort()
        #self.__available_gateways.reverse()

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
from sets import Set

#Define some constants - though these should come from the config
ESL_SERVER = '127.0.0.1'
ESL_PORT = 8021
ESL_AUTHENTICATION = 'ClueCon'


class CallHandler:
    
    __is_in_call = False
    __radio_station = None
    __ongoing_calls = []
    __ESLConnection = None
    __incoming_call_recipients = None
    __incoming_dtmf_recipients = None
    __outgoing_call_recipients = None
    __available_calls = None
    __media_playback_stop_recipients = None
    __gateways = dict()
    __available_gateways = []
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        t = threading.Thread(target=self.__handle_dtmf, args=())
        t.daemon = True
        t.start()
        self.__incoming_call_recipients = dict()
        self.__incoming_dtmf_recipients = dict()
        self.__outgoing_call_recipients = dict()
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
        #gws = Gateway.query.join(Gateway.stations_using_for_incoming).filter_by(id=self.__radio_station.id).all()
        for gw in gws:
            self.__gateways[str(gw.number_bottom)] = gw
            self.__available_gateways.append(gw.number_bottom)
            self.__available_gateways.sort()
            self.__available_gateways.reverse()
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
        print  self.__media_playback_stop_recipients.keys()

    def call(self, program_action, to_number, action, argument, time_limit):
        if to_number in self.__available_calls.keys():
            print self.__available_calls
            program_action.notify_call_answered(self.__available_calls[to_number])
        else:
            #call_command = 'originate sofia/gateway/goip/{0} &conference("hey")'.format(to_number)
            #originate {origination_caller_id_name='rootio',origination_caller_id_number=0417744801}sofia/gateway/utl/9510794451574 &conference("hey")
            gw = self.__gateways[str(self.__available_gateways.pop())[-9:]]
            call_command = 'originate {{{0}}}{1}/{2}{3} &conference("{4}_{5}")'.format(gw.extra_string, gw.sofia_string, gw.gateway_prefix, to_number, program_action.program.id, program_action.program.radio_station.id)
            print call_command
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
        print 'play command is ' + play_command
        return self.__do_ESL_command(play_command)
    
    def stop_play(self, call_UUID, content_location):
        stop_play_command = 'uuid_displace {0} stop \'{1}\''.format(call_UUID, content_location)
        print stop_play_command 
        return self.__do_ESL_command(stop_play_command)

    def speak(self, phrase, call_UUID):
        speak_command = 'speak stuff'
        return self.__do_ESL_command(speak_command) 
        
    
    def __report_answered(self, program_action):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_ANSWER")
        e = ESLConnection.recvEvent()
        if e:
            event_json_string = e.serialize('json')
            event_json = json.loads(event_json_string)
            self.__available_calls[str(event_json['Caller-Destination-Number'])[-10:]] = event_json
            program_action.notify_call_answered(event_json)

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
                        self.__media_playback_stop_recipients[event_json['Caller-Destination-Number']].notify_media_play_stop(e)
                except e:
                    print str(e)
                   
    def __claim_gateway(self, event_json):
        #if it is an incoming call
        if event_json['Caller-Destination-Number'] in self.__gateways:
            pass
            #self.__available_gateways.discard(event_json['Caller-Destination-Number'])
        #if it is an outbound call
        if event_json['Caller-Caller-ID-Number'] in self.__gateways:
            pass
            #self.__available_gateways.discard(event_json['Caller-Caller-ID-Number'])

    def __release_gateway(self, event_json):
        #if it was an incoming call
        if 'Caller-Destination-Number' in event_json and event_json['Caller-Destination-Number'][:-9] in self.__gateways.keys():
            self.__available_gateways.append(event_json['Caller-Destination-Number'])
            print "putting back {0}".format(event_json['Caller-Destination-Number'])
        #if it is an outbound call
        print "json is {0} but keys is {1}".format(event_json['variable_sip_from_user'][-9:], self.__gateways.keys())
        if 'variable_sip_from_user' in event_json and event_json['variable_sip_from_user'][-9:] in self.__gateways.keys():
            self.__available_gateways.append(int(event_json['variable_sip_from_user'][-9:]))
            print "putting back {0}".format(event_json['variable_sip_from_user'])
        self.__available_gateways.sort()
        self.__available_gateways.reverse()
        print self.__available_gateways

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 2:15:22 PM$"

from ESL import *
from rootio.config import *
import plivohelper
import threading

class CallHandler:
    
    __is_in_call = False
    __radio_station = None
    __ongoing_calls = []
    __ESLConnection = None
    __incoming_call_recipients = None
    __incoming_dtmf_recipients = None
    __media_playback_stop_recipients = None
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        t = threading.Thread(target=self.handle_dtmf, args=())
        t.daemon = True
        t.start()
        self.__incoming_call_recipients = dict()
        self.__incoming_dtmf_recipients = dict()
        self.__media_playback_stop_recipients = dict()
        #Create connection for DTMF 
        
    def __do_ESL_command(self, ESL_command):
        result = self.__ESLConnection.api(ESL_command)
        try:
            return result.getBody()
        except Exception, e:
            print str(e)
            return None

    def register_for_incoming_call(self, recipient, from_number):
        self.__incoming_call_recipients[from_number] = recipient

    def register_for_incoming_dtmf(self, recipient, from_number):
        self.__incoming_dtmf_recipients[from_number] = recipient

    def register_for_media_playback_stop(self, recipient, from_number):
        self.__media_playback_stop_recipients[from_number] = recipient

    def call(self, to_number, action, argument, time_limit):
        call_command = 'originate sofia/gateway/switch2voip/{0} &conference("hey")'.format(to_number)
        t = threading.Thread(target=self.__report_answered, args=())
        t.daemon = True
        t.start()
        return self.__do_ESL_command(call_command)

    def schedule_hangup(self, seconds, call_UUID):
        hangup_command = 'sched_hangup +{} {}'.format(seconds, call_UUID)
        return self.__do_ESL_command(hangup_command)
        
    def hangup(self, call_UUID):
        hangup_command = 'uuid_kill {}'.format(call_UUID)
        return self.__do_ESL_command(hangup_command)
           
    
    def play(self, file_location, call_UUID):
        play_command = 'uuid_displace {1} start {0}'.format(call_UUID, file_location)
        print 'play command is ' + play_command
        return self.__do_ESL_command(play_command)
    
    def stop_play(self, call_UUID, content_location):
        stop_play_command = 'uuid_displace {0} stop {1}'.format(call_UUID, content_location)
        print stop_play_command 
        return self.__do_ESL_command(stop_play_command)

    def speak(self, phrase, call_UUID):
        speak_command = 'speak stuff'
        return self.__do_ESL_command(speak_command) 
        
    
    def __report_answered(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_ANSWER")
        e = ESLConnection.recvEvent()
        if e:
            self.__radio_station.notify_call_answered(e)

    def request_conference(self, call_UUID, conference_UUID):
        break_command = 'break {0}'.format(conference_UUID)#currently al calls are added to conf. is there need to have a call not in conf?
        return self.__do_ESL_command(break_command) 

    def handle_dtmf(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "DTMF")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got DTMF event"
                self.__radio_station.notify_incoming_dtmf(e)
    
    def listen_for_media_play_stop(self):
        t = threading.Thread(target=self.handle_media_play_stop, args=())
        t.daemon = True
        t.start()
    
    def listen_for_incoming_calls(self):
        t = threading.Thread(target=self.handle_incoming_calls, args=())
        t.daemon = True
        t.start()

    def handle_incoming_calls(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "PHONE_RING")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got incoming call event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                try:
                    self.__incoming_call_recipients[event_json['from_number']].notify_incoming_call()
                except:
                    #indexing error, to number is unknown
    return

    def handle_media_play_stop(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "MEDIA_BUG_STOP")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got Media bug event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                try:
                    self.__media_playback_stop_recipients[event_json['from_number']].notify_media_play_stop(e)
                    #self.__radio_station.notify_media_play_stop(e)
                except:
                    #probably indexing error.

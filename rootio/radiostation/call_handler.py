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
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
    
    def __do_ESL_command(self, ESL_command):
        result = self.__ESLConnection.api(ESL_command)
        try:
            return result.getBody()
        except Exception, e:
            print str(e)
            return None

    def call(self, to_number, action, argument, time_limit):
        call_command = 'originate sofia/gateway/switch2voip/{0} &conference(%s)'.format(to_number)
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

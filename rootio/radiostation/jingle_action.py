# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json

class JingleAction:
    
    __argument = None
    __media = []
    start_time = None
    duration = None
    __is_streamed = False
    __program_handler = None
    __plivo = None
    __call_answer_info = None
    
    def __init__(self, argument,start_time, duration, is_streamed, program_handler):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__program_handler = program_handler
        self.__plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
        
    def start(self):
        self.__request_call()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__stop_jingle()
     
    def notify_call_answered(self, answer_info):
        self.__call_answer_info = json.loads(answer_info.serialize('json'))
        print self.__call_answer_info
        self.__play_jingle()
        
    def __request_call(self):
        raw_result = self.__program_handler.radio_station.request_call(self, '+256774712133',  'play', self.__argument, self.duration)
        result = raw_result.split(" ")
        print "Result of call is " + str(result)

    
    def __play_jingle(self): #play the media in the array
        if self.__is_streamed == True:
            result = self.__program_handler.radio_station.play_to_call(self.__call_answer_info['Channel-Call-UUID'], self.__argument)
            print 'result of jingle play is ' + result
    
    def __pause_jingle(self): #pause the media in the array
        pass
    
    def __stop_jingle(self):  #stop the media being played by the player
        result = self.__program_handler.radio_station.stop_playback(self.__call_answer_info['Channel-Call-UUID'], self.__argument)
        print 'result of jingle stop is ' + result    
    



# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json
from os import listdir
from os.path import isfile

class StreamAction:
    
    __argument = None
    __media = []
    start_time = None
    duration = None
    __is_streamed = False
    __program = None
    __plivo = None
    __call_answer_info = None
    
    def __init__(self, argument,start_time, duration, is_streamed, program):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__program = program
        self.__plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
        
    def start(self):
        self.__program.set_running_action(self)
        self.__request_call()
        #self.__play_media()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        print "media is now stopping"
        self.__stop_media()
     
    def notify_call_answered(self, answer_info):
        self.__call_answer_info = json.loads(answer_info.serialize('json'))
        print "I know...." #result
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'])
        
    def __load_media(self): #load the media to be played
        files = listdir(STREAM_DIRECTORY)
        self.__media.append(files[files.__len__() - 1])
    
    def __request_call(self):
        raw_result = self.__program.radio_station.request_call(self, '+256774536649',  'play', self.__argument, self.duration)
        result = raw_result.split(" ")
        print "Result of call is " + str(result)

    
    def __play_media(self, call_UUID): #play the media in the array
        
        if self.__is_streamed == True:
            result1 = self.__program.radio_station.play_to_call(call_UUID, self.__media.__len__() - 1)
            print 'result of play is ' + result1
            print "Media is now playing for " + str(self.duration) + " secs"
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        result = self.__program.radio_station.stop_playback(self.__media.__len__() - 1, self.__call_answer_info['Channel-Call-UUID'])
        print 'result of stop play is ' + result       
     



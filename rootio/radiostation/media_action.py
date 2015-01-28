# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json

class MediaAction:
    
    __argument = None
    __media = []
    start_time = None
    duration = None
    __is_streamed = False
    __radio_station = None
    __plivo = None
    
    def __init__(self, argument,start_time, duration, is_streamed, radio_station):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__radio_station = radio_station
        if radio_station == None:
            print "station is none 1"
        self.__plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
        
    def start(self):
        self.__request_call()
        #self.__play_media()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__stop_media()
     
    def notify_call_answered(self, answer_info):
        result = json.loads(answer_info.serialize('json'))
        print "I know...." #result
        self.__play_media(result['Channel-Call-UUID'])
        
    def __load_media(self): #load the media to be played
        pass
    
    def __request_call(self):
        raw_result = self.__radio_station.request_call(self, '+256794451574',  'play', self.__argument, self.duration)
        result = raw_result.split(" ")
        print "Result of call is " + str(result)

    
    def __play_media(self, call_UUID): #play the media in the array
        
        if self.__is_streamed == True:
            result1 = self.__radio_station.play_to_call(call_UUID, self.__argument)
            print 'result of play is ' + result1
            print "Media is now playing for " + str(self.duration) + " secs"
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        pass
    



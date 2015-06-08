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
    program = None
    __plivo = None
    __call_answer_info = None
    __call_handler = None    

    def __init__(self, argument,start_time, duration, is_streamed, program):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.program = program
        self.__call_handler = self.program.radio_station.call_handler        

    def start(self):
        self.program.set_running_action(self)
        self.__request_call()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        print "media is now stopping"
        self.__stop_media()
     
    def notify_call_answered(self, answer_info):
        self.__call_answer_info = answer_info
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'])
        
    def __load_media(self): #load the media to be played
        pass
    
    def __request_call(self):
        self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__argument, self.duration)
    
    def __play_media(self, call_UUID): #play the media in the array
        
        if self.__is_streamed == True:
            result1 = self.__call_handler.play(call_UUID, self.__argument)
            print 'result of play is ' + result1
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], self.__argument)
        print 'result of stop play is ' + result       
     



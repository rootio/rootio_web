# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json
from os import listdir
from rootio.radiostation.media.community_media import CommunityMedia

class InterludeAction:
    
    def __init__(self, argument, start_time, duration, is_streamed, program):
        self.__argument = argument
        self.program = program
        self.start_time = start_time
        self.__call_handler = self.program.radio_station.call_handler
        
    def start(self):
        self.program.set_running_action(self)
        self.__request_call()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__media_expected_to_stop = True
        self.__stop_media()
     
    def notify_call_answered(self, answer_info):
        self.__call_answer_info = answer_info
        self.__load_media()
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'], self.__media_index)
        self.__listen_for_media_play_stop()
        
    def __load_media(self): #load the media to be played
        community_media = CommunityMedia(self.__argument, self.program.radio_station.id)
        self.__media = community_media.get_media_files()
    
    def __request_call(self):
        raw_result = self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number,  'play', self.__argument, self.duration)

    def __play_media(self,call_UUID, media_index):
        logical_index = media_index % len(self.__media)
        result = self.__call_handler.play(call_UUID, self.__media[logical_index])
        print 'result of play ' + self.__media[logical_index] + ' is ' + result
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], self.__media_index)
        print 'result of stop play is ' + result       
     
    def notify_media_play_stop(self, media_stop_info):
        media_stop_json_string = media_stop_info.serialize("json")
        media_stop_json = json.loads(media_stop_json_string)
        if self.__media_index > len(self.__media) * 3: #all media has played thrice
            result = self.__call_handler.hangup(self.__call_answer_info['Channel-Call-UUID'])
            #deregister for media bug stop events
            print "result of hangup is " + result            
        elif not self.__media_expected_to_stop:
            self.__media_index = self.__media_index + 1
            self.__play_media(self.__call_answer_info['Channel-Call-UUID'], self.__media_index)
            
    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])
         


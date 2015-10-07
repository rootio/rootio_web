# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json

class MediaAction:
    
    def __init__(self, argument,start_time, duration, is_streamed, program, hangup_on_complete=False):
        self.__argument = argument
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.program = program
        self.__media_index = 0
        self.__media_expected_to_stop = False
        self.__hangup_on_complete = hangup_on_complete
        self.__call_handler = self.program.radio_station.call_handler        
        self.program.radio_station.logger.info("Done initing Media action for program {0}".format(self.program.name))

    def start(self):
        if self.__is_valid:
            self.program.set_running_action(self)
            self.__request_call()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__stop_media()
     
    def notify_call_answered(self, answer_info):
        self.program.radio_station.logger.info("Received call answer notification for Media action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'])
        self.__listen_for_media_play_stop()

    def __load_media(self): #load the media to be played
        pass
    
    def __request_call(self):
        self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__argument, self.duration)
    
    def __play_media(self, call_UUID): #play the media in the array
        if self.__is_streamed == True:
            self.program.radio_station.logger.info("Playing media {0} at position {1}".format(self.__media_index, self.__argument))
            result = self.__call_handler.play(call_UUID, self.__argument[self.__media_index])
            self.__media_index = self.__media_index + 1
            print 'result of play is ' + result
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        try:
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], self.__argument)
            print 'result of stop play is ' + result     
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return  
     
    def notify_media_play_stop(self, media_stop_info):
        if self.__media_index >= len(self.__argument):
            self.program.radio_station.logger.info("Played all media, stopping media play in Media action for {0}".format(self.program.name))
            self.__call_handler.deregister_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])
            if self.__hangup_on_complete:
                self.program.radio_station.logger.info("Hngup on complete is true for {0}".format(self.program.name)) 
                if media_stop_info["Media-Bug-Target"] == self.__argument[self.__media_index -1]: 
                    self.program.radio_station.logger.info("Deregistered, all good, about to order hangup for {0}".format(self.program.name))
                    self.__call_handler.hangup(self.__call_answer_info['Channel-Call-UUID'])
                
            self.__is_valid = False
        else:
            self.__play_media(self.__call_answer_info['Channel-Call-UUID'])

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])

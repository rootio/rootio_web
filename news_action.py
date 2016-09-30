# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import plivohelper
import json
from rootio.content.models import ContentTrack

class NewsAction:
    
    def __init__(self, track,start_time, duration, is_streamed, program, hangup_on_complete=False):
        self.__track = track
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.program = program
        self.__media_expected_to_stop = False
        self.__hangup_on_complete = hangup_on_complete
        self.__call_handler = self.program.radio_station.call_handler        
        self.program.log_program_activity("Done initing Media action for program {0}".format(self.program.name))

    def start(self):
        if self.__is_valid:
            self.program.set_running_action(self)
            call_result = self.__request_call()
            if call_result != True: #!!
                print "call_result is not true!!"
                self.stop()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__stop_media()
        self.program.notify_program_action_stopped(self)
     
    def notify_call_answered(self, answer_info):
        self.program.log_program_activity("Received call answer notification for Media action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'])
        self.__listen_for_media_play_stop()

    def __load_track(self): #load the media to be played
        self.__track = ContentTrack.query.filter(ContentTrack.id == self.__track_id).first()
    
    def __request_call(self):
        return self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__track.id, self.duration)
    
    def __play_media(self, call_UUID): #play the media in the array
        if self.__is_streamed == True:
            self.program.log_program_activity("Playing media {0}".format(self.__track.track_uploads[len(self.__track.track_uploads) -1].name))
            self.__listen_for_media_play_stop()
            
            #Always play the last file for news
            result = self.__call_handler.play(call_UUID, "/home/amour/test_media/{0}".format(self.__track.track_uploads[len(self.__track.track_uploads) -1].uri))
            self.program.log_program_activity('result of play is ' + result)
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        try:
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], self.__track.id)
            self.program.log_program_activity('result of stop play is ' + result )    
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return  
     
    def notify_media_play_stop(self, media_stop_info):
        self.program.radio_station.logger.info("Played all media, stopping media play in Media action for {0}".format(self.program.name))
        #self.__call_handler.deregister_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])
        if self.__hangup_on_complete:
            self.program.log_program_activity("Hangup on complete is true for {0}".format(self.program.name))
            if media_stop_info["Media-Bug-Target"] == "/home/amour/test_media/{0}".format(self.__track.track_uploads[len(self.__track.track_uploads) -1].uri): 
                self.program.log_program_activity("Deregistered, all good, about to order hangup for {0}".format(self.program.name))
                self.__call_handler.hangup(self.__call_answer_info['Channel-Call-UUID'])
                self.program.notify_program_action_stopped(self)
            self.__is_valid = False

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])

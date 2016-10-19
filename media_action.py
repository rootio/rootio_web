# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"
import os
from rootio.radio.models import ScheduledProgram
from rootio.content.models import ContentUploads
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
        self.__media_expected_to_stop = False
        self.__hangup_on_complete = hangup_on_complete
        self.__call_handler = self.program.radio_station.call_handler        
        self.program.log_program_activity("Done initing Media action for program {0}".format(self.program.name))

    def start(self):
        if self.__is_valid:
            self.program.set_running_action(self)
            episode_number = self.__get_episode_number(self.program.scheduled_program.program.id)
            self.__media = self.__load_media(episode_number)
            call_result = self.__request_call()
            if call_result != True: #!!
                print "call_result is not true!!"
                self.stop()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self, graceful=True):
        self.__stop_media()
        self.program.notify_program_action_stopped(self)
        self.program.scheduled_program.status = graceful
        self.program.db._model_changes = {}
        self.program.db.add(self.program.scheduled_program)
        self.program.db.commit()
     
    def notify_call_answered(self, answer_info):
        self.program.log_program_activity("Received call answer notification for Media action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-10:])
        self.__play_media(self.__call_answer_info['Channel-Call-UUID'])
        self.__listen_for_media_play_stop()

    def __load_media(self, episode_number): #load the media to be played
        media = self.program.db.query(ContentUploads).filter(ContentUploads.track_id == self.__argument).filter(ContentUploads.order == episode_number).first()
        return media
    
    def __get_episode_number(self, program_id):
        #Fix this below - Make RadioProgram inherit scheduled_program, rename it
        count = self.program.db.query(ScheduledProgram).filter(ScheduledProgram.status == True).filter(ScheduledProgram.program_id == program_id).count()
        return count + 1    

    def __request_call(self):
        return self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__argument, self.duration)
    
    def __play_media(self, call_UUID): #play the media in the array
        if self.__is_streamed == True:
            self.program.log_program_activity("Playing media {0}".format(self.__media.name))
            self.__listen_for_media_play_stop()
            result = self.__call_handler.play(call_UUID, os.path.join(DefaultConfig.CONTENT_DIR,self.__media.uri))
            self.program.log_program_activity('result of play is ' + result)
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        try:
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR,self.__media.uri))
            self.program.log_program_activity('result of stop play is ' + result )    
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return  
     
    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'][-10:])
        self.stop(False)


    def notify_media_play_stop(self, event_json):
        if event_json["Media-Bug-Target"] == os.path.join(DefaultConfig.CONTENT_DIR,self.__media.uri): 
            self.program.radio_station.logger.info("Stopping media play in Media action for {0}".format(self.program.name))
            #self.__call_handler.deregister_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])
            if self.__hangup_on_complete:
                self.program.log_program_activity("Hangup on complete is true for {0}".format(self.program.name))
                self.program.log_program_activity("Deregistered, all good, about to order hangup for {0}".format(self.program.name))
                self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'][-10:])
                self.__call_handler.hangup(self.__call_answer_info['Channel-Call-UUID'])
                self.stop()
            self.__is_valid = False

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])

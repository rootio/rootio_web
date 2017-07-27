# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from sqlalchemy import desc
from rootio.config import *
import json
from rootio.content.models import ContentPodcast, ContentPodcastDownload

class PodcastAction:
    
    def __init__(self, podcast_id, start_time, duration, program):
        self.__podcast_id = podcast_id
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__media_expected_to_stop = False
        self.__call_handler = self.program.radio_station.call_handler        
        self.program.log_program_activity("Done initing Media action for program {0}".format(self.program.name))

    def start(self):
        print "requesting call"
        call_result = self.__request_call()
        print call_result
        if call_result != True: #!!
            print "call_result is not true!!"
            self.stop(False)
    
    def pause(self):
        self.__pause_media()
    
    def stop(self, graceful=True, call_info=None):
        self.__stop_media(call_info)
        self.program.notify_program_action_stopped(graceful, call_info)
     
    def notify_call_answered(self, answer_info):
        self.program.log_program_activity("Received call answer notification for podcast action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-10:])
        self.__play_media(self.__call_answer_info)
        self.__listen_for_media_play_stop()

    def __load_podcast(self): #load the media to be played
        self.__podcast = self.program.db.query(ContentPodcast).filter(ContentPodcast.id == self.__podcast_id).first()
    
    def __request_call(self):
        return self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__podcast_id, self.duration)
    
    def __play_media(self, call_info): #play the media in the array
        self.__load_podcast()
        self.program.log_program_activity("Playing media {0}".format(self.__podcast.podcast_downloads[len(self.__podcast.podcast_downloads) -1].file_name))
        self.__listen_for_media_play_stop()
            
        #Always play the last file for news
        self.__last_podcast_download = self.program.db.query(ContentPodcastDownload).filter(ContentPodcastDownload.podcast_id == self.__podcast.id).order_by(desc(ContentPodcastDownload.date_created)).first()
        result = self.__call_handler.play(call_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR,'podcast', str(self.__podcast.id), self.__last_podcast_download.file_name))
        self.program.log_program_activity('result of play is ' + result)
        if result.split(" ")[0] != "+OK":
           self.stop(False, call_info)
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self, event_json):  #stop the media being played by the player
        try:
            self.program.log_program_activity("Deregistered, all good, about to order hangup for {0}".format(self.program.name))
            self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'][-10:])
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR,'podcast', str(self.__podcast.id), self.__last_podcast_download.file_name))
            self.program.log_program_activity('result of stop play is ' + result )    
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return  

    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        self.stop(False, event_json)
     
    def notify_media_play_stop(self, event_json):
        self.program.radio_station.logger.info("Played all media, stopping media play in Media action for {0}".format(self.program.name))
        self.program.log_program_activity("Hangup on complete is true for {0}".format(self.program.name))
        if event_json["Media-Bug-Target"] == os.path.join(DefaultConfig.CONTENT_DIR,'podcast', str(self.__podcast.id), self.__last_podcast_download.file_name): 
            self.stop(True, event_json) #program.notify_program_action_stopped(self)
        self.__is_valid = False

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])

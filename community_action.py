# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

from rootio.config import *
import json
from rootio.content.models import CommunityContent

class CommunityAction:
    
    def __init__(self, type_code, start_time, duration, program):
        self.__type_code = type_code
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__media_expected_to_stop = False
        self.__media_index = 0
        self.__call_handler = self.program.radio_station.call_handler        
        self.program.log_program_activity("Done initing Media action for program {0}".format(self.program.name))

    def start(self):
        print "requesting call"
        call_result = self.__request_call()
        print call_result
        if call_result != True: #!!
            print "call_result is not true!!"
            self.stop(False)
    
    def stop(self, graceful=True, call_info=None):
        self.__media_expected_to_stop = True
        self.__stop_media(call_info)
        self.program.notify_program_action_stopped(graceful, call_info)
     
    def notify_call_answered(self, answer_info):
        self.program.log_program_activity("Received call answer notification for Media action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-10:])
        self.__play_media(self.__call_answer_info, self.__media_index)
        self.__listen_for_media_play_stop()

    def __load_track(self): #load the media to be played
        self.__content = self.program.db.query(CommunityContent).filter(CommunityContent.type_code==self.__type_code).filter(CommunityContent.station_id ==self.program.radio_station.station.id).all()

    def __request_call(self):
        return self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__type_code, self.duration)
    
    def __play_media(self, call_info, idx): #play the media in the array
        self.__load_track()
        self.program.log_program_activity("Playing media {0}".format(self.__content[idx].message))
            
        result = self.__call_handler.play(call_info['Channel-Call-UUID'], os.path.join(DefaultConfig.CONTENT_DIR,"community-content",str(self.program.radio_station.station.id), str(self.__type_code),self.__content[idx].message))
        self.program.log_program_activity('result of play is ' + result)
        if result.split(" ")[0] != "+OK":
           self.stop(False, call_info)
    
    def __stop_media(self, event_json):  #stop the media being played by the player
        try:
            self.program.log_program_activity("Deregistered, all good, about to order hangup for {0}".format(self.program.name))
            self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'][-10:])
            self.__call_handler.deregister_for_media_playback_stop(self, event_json['Caller-Destination-Number'][-10:])
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'], self.__content[self.__media_index])
            self.program.log_program_activity('result of stop play is ' + result )    
        except Exception, e:
            self.program.radio_station.logger.error(str(e))
            return  

    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        self.stop(False, event_json)
     
    def notify_media_play_stop(self, event_json):
        if event_json["Media-Bug-Target"] == os.path.join(DefaultConfig.CONTENT_DIR,"community-content",str(self.program.radio_station.station.id), str(self.__type_code),self.__content[self.__media_index % len(self.__content)].message): #its our media stopping, not some other media
            if self.__media_index >= len(self.__content) * 3: #all media has played
                self.program.radio_station.logger.info("Played all media thrice in Interlude action for {0}, hanging up".format(self.program.name))
                self.stop(True, event_json)
            elif not self.__media_expected_to_stop:
                self.__media_index = self.__media_index + 1
                self.__play_media(self.__call_answer_info, self.__media_index % len(self.__content))        

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,self.__call_answer_info['Caller-Destination-Number'])

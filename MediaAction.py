# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:29:19 PM$"

class MediaAction:
    
    __argument = None
    __media = []
    _start_time = None
    _duration = None
    
    def __init__(self, argument,start_time, duration):
        self.__argument = argument
        self._start_time = start_time
        self._duration = duration
        
    def start(self):
        self.__play_media()
    
    def pause(self):
        self.__pause_media()
    
    def stop(self):
        self.__stop_media()
    
    def __load_media(self): #load the media to be played
        pass
    
    def __play_media(self): #play the media in the array
        print "Media is now playing for " + str(self._duration) + " secs"
    
    def __pause_media(self): #pause the media in the array
        pass
    
    def __stop_media(self):  #stop the media being played by the player
        pass
    



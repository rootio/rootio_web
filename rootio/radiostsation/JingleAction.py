# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:55:14 PM$"

class JingleAction:
    
    argument = None
    start_time = None
    duration = None
    __radio_station = None
    
    def __init__(self, argument, start_time, duration, is_streamed, radio_station):
        self.argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__radio_station = radio_station
        
    def start(self):
        self.__play_jingle()
    
    def pause(self):
        self.__pause_jingle()
    
    def stop(self):
        self.__stop_jingle()
    
    def __load_jingle(self): #load the jingle to be played
        pass
    
    def __play_jingle(self): #Play the Jingle
        print "Jingle starting for " + str(self.duration) + " secs"
        pass
    
    def __pause_jingle(self): #pause the jingle in case of any overriding actions
        pass
    
    def __stop_jingle(self):  #stop the jingle when necessary
        pass

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:51:00 PM$"

class OutCallAction:
    
    __argument = None
    __media = []
    
    def __init__(self, argument):
        self.argument = argument
        
    def start(self):
        self.__call_number(self.__argument)
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.__hangup_call()
    
     
    def __call_number(self): #call the number specified thru plivo
        pass
    
    def __hold_call(self): #put ongoing call on hold
        pass
    
    def __hangup_call(self):  #hangup the ongoing call
        pass

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Dec 20, 2014 8:04:46 PM$"

class MenuStage:

    WELCOME=1
    VALIDITY=2
    RECORDING=3
    GOODBYE=4

class IVRHandler:
    __radio_station
    __call_info
    __menu_stage
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__menu_stage = MenuStage.WELCOME

    def handle_incoming_call(self, call_info)
        self.__call_info = call_info
        #unpark the call
        #play the corresponding prompts  
  
    def notify_incoming_dtmf(self, dtmf_info):
        #get the digit from the dtmf
        if self.__menu_stage == MenuStage.WELCOME:
            #play the welcome message
            self.__menu_stage = MenuStage.VALIDITY:
        elif self.__menu_stage == MenuStage.VALIDITY:
            
 
        

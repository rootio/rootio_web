# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Dec 20, 2014 8:04:46 PM$"

class IVRHandler:
    
    __action = None
    __argument = None
    __call_handler = None
    __current_node = None
    __call_UUID = None
    
    def __init__(self, IVR_info, call_handler, call_UUID):
        self.__call_handler = call_handler
        self.__call_UUID = call_UUID
        self.__load_IVR_menu(IVR_info)
        
    def __load_IVR_menu(self, IVR_info):
        pass
    
    def handle_IVR(self, call_UUID):
        DTMF = self.__listen_for_DTMF()
        self.__handle_DTMF(DTMF)
        
    def __listen_for_DTMF(self):
        pass
        
    def __handle_DTMF(self, DTMF):
        #listen for DTMF
        self.__current_node = self.__current_node[DTMF]
        if self.__current_node['action'] == 'speak':
            self.__call_handler.speak(self.__current_node['argument'], self.__call_UUID)
            return
        if self.__current_node == 'record':
            self.__call_handler.speak(self.__current_node['argument'], self.__call_UUID)
            #record the call
            return
        #Terminate the call if the menu has no further children
         
        

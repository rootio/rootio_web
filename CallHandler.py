# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 2:15:22 PM$"
from config import *
import plivohelper

class CallHandler:
    
    __is_in_call = False
    __radio_station = None
    __ongoing_calls = []
    __plivo = None
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
        
    def call(self, to_number, time_limit, from_number, gateway, answered=ANSWERED,extra_dial_string=EXTRA_DIAL_STRING):
        call_params = {
            'From': from_number, # Caller Id
            'To' : to_number, # User Number to Call
            'Gateways' : gateway, # Gateway string to try dialing separated by comma. First in list will be tried first
            'GatewayCodecs' : "", # Codec string as needed by FS for each gateway separated by comma
            'GatewayTimeouts' : "20,20", # Seconds to timeout in string for each gateway separated by comma
            'GatewayRetries' : "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
            'ExtraDialString' : extra_dial_string,
            'AnswerUrl' : answered+'answered/',
            'HangupUrl' : answered+'hangup/',
            'RingUrl' : answered+'ringing/',
            'TimeLimit' : time_limit,
            #'HangupOnRing': '0',
        }
        #Perform the Call on the Rest API
        try:
            result = self.__plivo.call(call_params)
            if result['Success'] == True:
                self.__ongoing_calls.insert(result)
            return result
        except Exception, e:
            print str(e)
            return None
    """
    Overload of call for easier calling assuming  with specified time limit
    """
    def call(self, to_number, time_limit):
        return call(to_number, time_limit, self.__station._station.cloud_phone_id, self.__station._station.gateway)#fix this
    
    """
    Overload of call for easier calling assuming  with no time limit
    """
    def call(self, to_number):
        return call(to_number, '0')
        
    def hangup(self, request_UUID):
        hangup_params = {'RequestUUID' : request_UUID }
        result = self.__plivo.hangup_call(hangup_params)
        if result['Success'] == True:
            #self.__ongoing_calls.remove() remove the call from the ongoing calls
    
   def play(self, content_location, callUUID):
       play_params = {"CallUUID" : callUUID, "Sounds" : content_location}
       result = self.__plivo.play(play_params)
       return result
        
        
    

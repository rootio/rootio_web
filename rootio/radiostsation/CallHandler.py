# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 2:15:22 PM$"
from rootio.config import *
import plivohelper

class CallHandler:
    
    __is_in_call = False
    __radio_station = None
    __ongoing_calls = []
    __plivo = None
    
    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
        
    def call(self, to_number, action, argument, time_limit):
        call_params = {
            'From': '1234', #from_number, #get station id
            'To' : to_number, # User Number to Call
            'Gateways' : 'sofia/gateway/switch2voip/', #gateway, # Gateway string to try dialing separated by comma. First in list will be tried first. get station gateway
            'GatewayCodecs' : "", # Codec string as needed by FS for each gateway separated by comma
            'GatewayTimeouts' : "20,20", # Seconds to timeout in string for each gateway separated by comma
            'GatewayRetries' : "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
            'ExtraDialString' : 'bridge_early_media=true,hangup_after_bridge=true',
            'AnswerUrl' : REST_API_URL + '/' + API_VERSION + '/' + self.get_answer_url(action) + '?argument=' + argument,
            #'HangupUrl' : answered+'hangup/',
            #'RingUrl' : answered+'ringing/',
            'CallUrl' : 'http://demo.rootio.org/plivotest/v0.1/Call/',
            'TimeLimit' : time_limit,
            #'argument' : argument
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
        
    def hangup(self, request_UUID):
        hangup_params = {'RequestUUID' : request_UUID }
        result = self.__plivo.hangup_call(hangup_params)
        if result['Success'] == True:
            pass  #self.__ongoing_calls.remove() remove the call from the ongoing calls
        return result
           
    
    def play(self, content_location, callUUID):
        play_params = {"CallUUID" : callUUID, "Sounds" : content_location}
        result = self.__plivo.play(play_params)
        return result
    
    def speak(self, phrase, call_UUID):
        speak_params = {"CallUUID" : call_UUID, "Phrase" : phrase}
        result = self.__plivo.speak(speak_params)
        return result
        
    def get_answer_url(self, desired_action):
        actions = {'play' : 'answered_for_play/', 'speak' : 'answered_for_speak/'}
        action_url = actions[desired_action]
        if action_url == None :
            return 'answered/'
        return action_url
      

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 26, 2014 11:24:58 AM$"

if __name__ == "__main__":
    print "Hello World"


import plivohelper
from time import sleep

import ..rootio.config 


ANSWERED = 'http://127.0.0.1:5000/'
SOUNDS_ROOT = 'http://176.58.125.166/~csik/sounds/'
EXTRA_DIAL_STRING = "bridge_early_media=true,hangup_after_bridge=true"

def call(to_number, from_number, gateway, answered=ANSWERED,extra_dial_string=EXTRA_DIAL_STRING):
    plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)
    call_params = {
        'From': from_number, # Caller Id
        'To' : to_number, # User Number to Call
        'Gateways' : gateway, # Gateway string to try dialing separated by comma. First in list will be tried first
        'GatewayCodecs' : "", # Codec string as needed by FS for each gateway separated by comma
        'GatewayTimeouts' : "20,20",      # Seconds to timeout in string for each gateway separated by comma
        'GatewayRetries' : "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
        'ExtraDialString' : extra_dial_string,
        'AnswerUrl' : answered+'answered/',
        'HangupUrl' : answered+'hangup/',
        'RingUrl' : answered+'ringing/',
        #'TimeLimit' : '15',
    	#'HangupOnRing': '0',
    }
    request_uuid = ""

    #Perform the Call on the Rest API
    try:
        result = plivo.call(call_params)
        logger.info(str(result))
        return result
    except Exception, e:
        print str(e)
        return "Error"

if __name__ == "__main__":
    print "Hello World"
    call("+256794451574", "123", "sofia/gateway/switch2voip/")

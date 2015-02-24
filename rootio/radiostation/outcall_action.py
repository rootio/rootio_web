# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:51:00 PM$"

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
from interlude_action import InterludeAction
import json

class PhoneStatus:

    REJECTING=1
    QUEUING=2
    ANSWERING=3
    CONFERENCING=4
    IVR=5
    RINGING=6

class OutcallAction:
    
    __argument = None
    start_time = None
    duration = None
    __is_streamed = False
    __warning_time = None
    ___program = None
    __scheduler = None
    __call_details = None
    __station_call_available = False 
    __station_call_answer_info = None
    __host_call_answer_info = None
    __phonne_status = None
    __interested_participants = None
    
    def __init__(self, argument, start_time, duration, is_streamed, warning_time, program):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__warning_time = warning_time
        self.__program = program
        self.__scheduler = BackgroundScheduler()
        self.__phone_status = PhoneStatus.QUEUING
        self.__interested_participants = []
        
    def start(self):
        #self.__program.set_running_action(self)
        self.__request_call()
        self.__scheduler.start()
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.hangup_call()
        
    def __request_call(self):
        raw_result = self.__program.radio_station.request_call(self, '+256718451574',  'play', self.__argument, self.duration)
        result = raw_result.split(" ")
        print "Result of call is " + str(result)

    def __call_host_number(self): #call the number specified thru plivo
        result = self.__call_details = self.__program.radio_station.request_call(self, self.__argument, None, None, self.duration) 
        print "result of host call is " + str(result)
    
    def __request_conference_bridge(self, call_UUID, conference_UUID):
        result = self.__program.radio_station.request_conference(call_UUID, conference_UUID)   
        print result
        #Tell host that they are now live on air?

    def notify_call_answered(self, answer_info):
        if self.__station_call_available == False:#This notification is from answering the station call
            self.__station_call_available = True
            self.__station_call_answer_info = json.loads(answer_info.serialize('json'))
            self.__call_host_number() 
        else:#This notification is from answering the host call
            self.__host_call_answer_info = json.loads(answer_info.serialize('json'))
            result1 = self.__schedule_warning()
            result2 = self.__schedule_hangup()

    def warn_number(self): 
        seconds = self.duration - self.__warning_time
        phrase = "This call will end in {0} seconds".format({seconds})
        result = self.__program.radio_station.speak_to_call(self.__host_call_answer_info['Channel-Call-UUID'], phrase)
        print "result of warning is " + result;
    
    def __pause_call(self):#hangup and schedule to call later
        self.hangup_call()
        interlude_action = InterludeAction("greetings", self.__program)
        interlude_action.start()
        #self.__schedule_host_callback()
       
    
    def __hold_call(self): #put ongoing call on hold
        print "We should be holding now"
    
    def hangup_call(self):  #hangup the ongoing call
        result = self.__program.radio_station.hangup_call(self.__host_call_answer_info['Channel-Call-UUID'])
        print "result of hangup is " + result
    
    def handle_dtmf(self, dtmf_info):
        dtmf_json_string = dtmf_info.serialize('json')
        dtmf_json = json.loads(dtmf_json_string)
        dtmf_digit = dtmf_json["DTMF-Digit"]
        if dtmf_digit == "1":
            self.hangup_call() 
        elif dtmf_digit == "2":#stop the music, put this live on air
            self.__program.set_running_action(self)
   
        elif dtmf_digit == "3":#put the station =in auto_answer
            self.__phone_status = PhoneStatus.ANSWERING

        elif dtmf_digit == "4":#disable auto answer, reject and record all incoming calls
            self.__phone_status = PhoneStatus.REJECTING

        elif dtmf_digit == "5":#dequeue and call from queue of calls that were rejected
            pass

        elif dtmf_digit == "6":#Take a 5 min music break
            self.__pause_call()

    def handle_incoming_call(self, call_info):
        if self.__phone_status == PhoneStatus.ANSWERING: #answer the phone call, join it to the conference
            pass
        elif self.__phone_status == PhoneStatus.QUEUING: #Hangup the phone, call back later
            self.__interested_participants.append(call_info['From'])
            self.__program.radio_station.hangup_call(call_info['Channel-Call-UUID']);
            pass

        elif self.__phone_status == PhoneStatus.REJECTING: #Hangup the call
            self.__program.radio_station.hangup_call(call_info['Channel-Call-UUID']);
 
    def __schedule_host_callback(self):
        time_delta = timedelta(seconds=60) #five minutes
        now = datetime.utcnow()
        callback_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'__call_host_number'), 'date', None, None, None, 'host_callback', 1, 0, 1, callback_time)
    
    def __schedule_warning(self):
        time_delta = timedelta(seconds=self.__warning_time)
        now = datetime.utcnow()
        warning_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'warn_number'), 'date', None, None, None, 'host_warning', 1, 0, 1, warning_time)

    def __schedule_hangup(self):
        time_delta = timedelta(seconds=self.duration)
        now = datetime.utcnow()
        hangup_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'hangup_call'), 'date', None, None, None, 'host_hangup', 1, 0, 1, hangup_time)   

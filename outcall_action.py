# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:51:00 PM$"

from apscheduler.scheduler import Scheduler
from datetime import timedelta, datetime
from interlude_action import InterludeAction
from sets import Set
import json

class PhoneStatus:

    REJECTING=1
    QUEUING=2
    ANSWERING=3
    CONFERENCING=4
    IVR=5
    RINGING=6

class OutcallAction:
    
    def __init__(self, argument, start_time, duration, is_streamed, warning_time, program, hangup_on_complte):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__warning_time = warning_time
        self.program = program
        self.__scheduler = Scheduler()
        self.__call_handler = self.program.radio_station.call_handler
        self.__phone_status = PhoneStatus.QUEUING
        self.__interested_participants = Set([])
        self.__interested_participants.add("30718451574")
        self.__hangup_on_complete = hangup_on_complete

    def start(self):
        self.__program.set_running_action(self)
        self.__request_call()
        self.__scheduler.start()
        self.__call_handler.register_for_incoming_calls(self, '1003')
        self.__call_handler.register_for_incoming_dtmf(self, self.__argument)
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.hangup_call()
        
    def __request_call(self):
        self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__argument, self.duration)

    def call_host_number(self): #call the number specified thru plivo
        result = self.__call_handler.call(self, self.__argument, None, None, self.duration) 
        print "result of host call is " + str(result)
    
    def __request_conference_bridge(self, call_UUID, conference_UUID):
        result = self.__call_handler.request_conference(call_UUID, conference_UUID)   
        print result
        #Tell host that they are now live on air?

    def notify_call_answered(self, answer_info):
        if self.__station_call_available == False:#This notification is from answering the station call
            self.__station_call_available = True
            self.__station_call_answer_info = answer_info
            self.call_host_number() 
        else:#This notification is from answering the host call
            self.__host_call_answer_info = answer_info
            result1 = self.__schedule_warning()
            result2 = self.__schedule_hangup()

    def warn_number(self): 
        seconds = self.duration - self.__warning_time
        phrase = "This call will end in {0} seconds".format({seconds})
        result = self.__call_handler.speak(self.__host_call_answer_info['Channel-Call-UUID'], phrase)
        print "result of warning is " + result;
    
    def __pause_call(self):#hangup and schedule to call later
        #self.hangup_call()
        interlude_action = InterludeAction("greetings", self.program)
        interlude_action.start()
        self.__schedule_host_callback()
       
    
    def __hold_call(self): #put ongoing call on hold
        print "We should be holding now"
    
    def hangup_call(self):  #hangup the ongoing call
        result = self.__call_handler.hangup(self.__host_call_answer_info['Channel-Call-UUID'])
        print "result of hangup is " + result
        if self.__hangup_on_complete:
            result = self.__call_handler.hangup(self.__station_call_answer_info['Channel-Call-UUID'])
        print "result of station hangup is " + result
    
    def notify_incoming_dtmf(self, dtmf_info):
        dtmf_json = dtmf_info
        dtmf_digit = dtmf_json["DTMF-Digit"]
        if dtmf_digit == "1":
            self.hangup_call() 
        elif dtmf_digit == "2":#stop the music, put this live on air
            self.program.set_running_action(self)
   
        elif dtmf_digit == "3":#put the station =in auto_answer
            self.__phone_status = PhoneStatus.ANSWERING

        elif dtmf_digit == "4":#disable auto answer, reject and record all incoming calls
            self.__phone_status = PhoneStatus.REJECTING

        elif dtmf_digit == "5":#dequeue and call from queue of calls that were rejected
            for caller in self.__interested_participants:
                self.__call_handler.call(self, caller, None, None, self.duration)
                self.__interested_participants.discard(caller)
                return

        elif dtmf_digit == "6":#Take a 5 min music break
            self.__pause_call()

    def notify_incoming_call(self, call_info):
        if self.__phone_status == PhoneStatus.ANSWERING: #answer the phone call, join it to the conference
            pass
        elif self.__phone_status == PhoneStatus.QUEUING: #Hangup the phone, call back later
            self.__interested_participants.add(call_info['Caller-Caller-ID-Number'])
            print self.__interested_participants
            self.__call_handler.hangup(call_info['Channel-Call-UUID']);
            pass

        elif self.__phone_status == PhoneStatus.REJECTING: #Hangup the call
            self.__call_handler.hangup(call_info['Channel-Call-UUID']);
 
    def __schedule_host_callback(self):
        time_delta = timedelta(seconds=60) #one minutes
        now = datetime.utcnow()
        callback_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'call_host_number'), callback_time)
    
    def __schedule_warning(self):
        time_delta = timedelta(seconds=self.__warning_time)
        now = datetime.utcnow()
        warning_time = now + time_delta
        self.__scheduler.add_date_job(getattr(self,'warn_number'), warning_time)

    def __schedule_hangup(self):
        time_delta = timedelta(seconds=self.duration)
        now = datetime.utcnow()
        hangup_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'hangup_call'), hangup_time)   

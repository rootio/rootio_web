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
    
    def __init__(self, argument, start_time, duration, is_streamed, warning_time, program, hangup_on_complete):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__warning_time = warning_time
        self.program = program
        self.__scheduler = Scheduler()
        self.__available_calls = dict()
        self.__call_handler = self.program.radio_station.call_handler
        self.__phone_status = PhoneStatus.QUEUING
        self.__interested_participants = Set([])
        self.__hangup_on_complete = hangup_on_complete
        

    def start(self):
        self.program.set_running_action(self)
        self.request_host_call()
        self.__scheduler.start()
        self.__community_call_UUIDs = dict()
        self.__call_handler.register_for_incoming_calls(self)
        self.__call_handler.register_for_incoming_dtmf(self, str(self.__argument))
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.hangup_call()
        
    def request_host_call(self):
        result = self.__call_handler.call(self, self.__argument, None, None, self.duration)
        print "result of host call is " + result;

    def request_station_call(self): #call the number specified thru plivo
        result = self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__argument, self.duration)
        print "result of host call is " + str(result)
    
    def notify_call_answered(self, answer_info):
        if self.__argument not in self.__available_calls:
            self.__available_calls[answer_info['Caller-Destination-Number'][-10:]] = answer_info
            self.request_station_call() 
        else:#This notification is from answering the host call
            self.__available_calls[answer_info['Caller-Destination-Number'][-10:]] = answer_info
            result1 = self.__schedule_warning()
            result2 = self.__schedule_hangup()
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-10:])

    def warn_number(self): 
        seconds = self.duration - self.__warning_time
        phrase = "This call will end in {0} seconds".format({seconds})
        result = self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'], '/home/amour/media/call_warning.mp3')
        print "result of warning is " + result;
    
    def __pause_call(self):#hangup and schedule to call later
        self.__schedule_host_callback()
        self.hangup_call()
    
    def notify_call_hangup(self, event_json):
        if 'Caller-Destination-Number' in event_json and event_json['Caller-Destination-Number'] in self.__community_call_UUIDs: #a community caller is hanging up
            del self.__community_call_UUIDs[event_json['Caller-Destination-Number']]
            self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'])
        else: #It is a hangup by the station or the host
            self.hangup_call() #clean this later

    def __hold_call(self): #put ongoing call on hold
        print "We should be holding now"
    
    def hangup_call(self):  #hangup the ongoing call
        for available_call in self.__available_calls:
            self.__call_handler.deregister_for_call_hangup(self, available_call)
            result = self.__call_handler.hangup(self.__available_calls[available_call]['Channel-Call-UUID'])
            #del self.__available_calls[available_call]
            print "result of hangup is " + result
        self.__available_calls = dict() #empty available calls. they all are hung up
        
    def notify_incoming_dtmf(self, dtmf_info):
        dtmf_json = dtmf_info
        dtmf_digit = dtmf_json["DTMF-Digit"]
        if dtmf_digit == "1":
            self.hangup_call() 
        elif dtmf_digit == "2":#stop the music, put this live on air
            self.program.set_running_action(self)
   
        elif dtmf_digit == "3":#put the station =in auto_answer
            if self.__phone_status != PhoneStatus.ANSWERING:
                self.__phone_status = PhoneStatus.ANSWERING
                self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'],'/home/amour/media/incoming_auto_answer.mp3')
            else:
                self.__phone_status = PhoneStatus.REJECTING
                self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'], '/home/amour/media/incoming_reject.mp3')

        elif dtmf_digit == "4":#disable auto answer, reject and record all incoming calls
            if self.__phone_status != PhoneStatus.QUEUING:
                self.__phone_status = PhoneStatus.QUEUING
                self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'], '/home/amour/media/incoming_queued.mp3')
            else:
                self.__phone_status = PhoneStatus.REJECTING
                self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'], '/home/amour/media/incoming_reject.mp3')

        elif dtmf_digit == "5":#dequeue and call from queue of calls that were rejected
            for caller in self.__interested_participants:  
                result = self.__call_handler.call(self, caller, None, None, self.duration)
                print "result of participant call is {0}".format(str(result))
                self.__community_call_UUIDs[caller] = result.split(" ")[-1]
                self.__call_handler.register_for_call_hangup(self, caller)
                self.__interested_participants.discard(caller)
                return

        elif dtmf_digit == "6":#terminate the current caller
            for community_call_UUID in self.__community_call_UUIDs:
                self.__call_handler.hangup(self.__community_call_UUIDs[community_call_UUID])
            pass

        elif dtmf_digit == "7":#Take a 5 min music break
            self.__pause_call()

    def notify_incoming_call(self, call_info):
        if self.__phone_status == PhoneStatus.ANSWERING: #answer the phone call, join it to the conference
            if len(self.__community_call_UUIDs) == 0:
                self.__call_handler.bridge_incoming_call(call_info['Channel-Call-UUID'], self)
                self.__call_handler.register_for_call_hangup(self, call_info['Caller-Destination-Number'])
                self.__community_call_UUIDs[call_info['Caller-Destination-Number']] = call_info['Channel-Call-UUID']
        elif self.__phone_status == PhoneStatus.QUEUING: #Hangup the phone, call back later
            self.__interested_participants.add(call_info['Caller-ANI'])
            self.__call_handler.play(self.__available_calls[self.__argument]['Channel-Call-UUID'], '/home/amour/media/incoming_new_caller.mp3')
            print self.__interested_participants
            self.__call_handler.hangup(call_info['Channel-Call-UUID']);

        elif self.__phone_status == PhoneStatus.REJECTING: #Hangup the call
            self.__call_handler.hangup(call_info['Channel-Call-UUID']);
 
    def __schedule_host_callback(self):
        time_delta = timedelta(seconds=300) #one minutes
        now = datetime.utcnow()
        callback_time = now + time_delta
        #self.__scheduler.add_date_job(getattr(self,'call_host_number'), callback_time)
        self.__scheduler.add_date_job(getattr(self,'request_host_call'), callback_time)    

    def __schedule_warning(self):
        time_delta = timedelta(seconds=self.__warning_time)
        now = datetime.utcnow()
        warning_time = now + time_delta
        self.__scheduler.add_date_job(getattr(self,'warn_number'), warning_time)

    def __schedule_hangup(self):
        time_delta = timedelta(seconds=self.duration)
        now = datetime.utcnow()
        hangup_time = now + time_delta
        self.__scheduler.add_date_job(getattr(self,'hangup_call'), hangup_time)   

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

from rootio.radio.models import Person
from rootio.telephony.models import PhoneNumber

class PhoneStatus:

    REJECTING=1
    QUEUING=2
    ANSWERING=3
    CONFERENCING=4
    IVR=5
    RINGING=6

class OutcallAction:
    
    def __init__(self, host_id, start_time, duration, program):
        self.__host_id = host_id
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__scheduler = Scheduler()
        self.__available_calls = dict()
        self.__call_handler = self.program.radio_station.call_handler
        self.__phone_status = PhoneStatus.QUEUING
        self.__interested_participants = Set([])

    def start(self):
        self.__in_talkshow_setup = True
        self.__host = self.__get_host(self.__host_id)
        #self.program.set_running_action(self)
        self.request_host_call()
        self.__scheduler.start()
        self.__community_call_UUIDs = dict()
        self.__call_handler.register_for_incoming_calls(self)
        self.__call_handler.register_for_incoming_dtmf(self, str(self.__host.phone.raw_number))
        self.__call_handler.register_for_host_call(self, str(self.__host.phone.raw_number))
    
    def pause(self):
        self.__hold_call()
    
    def stop(self, graceful=True, call_info=None):
        self.hangup_call()
        #Stop scheduler
        self.__scheduler.shutdown()
        #deregister from any triggers
        self.__call_handler.deregister_for_incoming_calls(self)
        self.__call_handler.deregister_for_incoming_dtmf(str(self.__host_id))
        self.program.notify_program_action_stopped(graceful, call_info)

    def __get_host(self, host_id):
        host = self.program.db.query(Person).filter(Person.id == host_id).first()
        return host
        
    def request_host_call(self):
        self.__in_talkshow_setup = True
        result = self.__call_handler.call(self, self.__host.phone.raw_number, None, None, 15) #call ends in 15 mins max
        print "result of host call is " + str(result);

    def request_station_call(self): #call the number specified thru plivo
        result = self.__call_handler.call(self, self.program.radio_station.station.transmitter_phone.number, 'play', self.__host.phone.raw_number, self.duration)
        print "result of host call is " + str(result)
    
    def notify_call_answered(self, answer_info):
        if self.__host.phone.raw_number not in self.__available_calls:
            self.__available_calls[answer_info['Caller-Destination-Number'][-10:]] = answer_info
            self.__inquire_host_readiness()
        else:#This notification is from answering the host call
            self.__available_calls[answer_info['Caller-Destination-Number'][-10:]] = answer_info
            result1 = self.__schedule_warning()
            result2 = self.__schedule_hangup()
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-10:])

    def warn_number(self): 
        seconds = self.duration - self.__warning_time
        if self.__host.phone.raw_number in self.__available_calls and 'Channel-Call-UUID' in self.__available_calls[self.__host.phone.raw_number]:
            result = self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'], '/home/amour/media/call_warning.mp3')
            print "result of warning is " + result;
    
    def __pause_call(self):#hangup and schedule to call later
        self.__schedule_host_callback()
        self.hangup_call()
    
    def notify_call_hangup(self, event_json):
        if 'Caller-Destination-Number' in event_json and event_json['Caller-Destination-Number'] in self.__community_call_UUIDs: #a community caller is hanging up
            del self.__community_call_UUIDs[event_json['Caller-Destination-Number']]
            self.__call_handler.deregister_for_call_hangup(self, event_json['Caller-Destination-Number'])
        else: #It is a hangup by the station or the host
            self.stop(True)
            #self.hangup_call() #clean this later

    def __inquire_host_readiness(self):
        self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'],'/home/amour/media/inquire_host_readiness.mp3')

    def hangup_call(self):  #hangup the ongoing call
        for available_call in self.__available_calls:
            self.__call_handler.deregister_for_call_hangup(self, available_call)
            self.__call_handler.hangup(self.__available_calls[available_call]['Channel-Call-UUID'])
        self.__available_calls = dict() #empty available calls. they all are hung up
        
    def notify_incoming_dtmf(self, dtmf_info):
        dtmf_json = dtmf_info
        dtmf_digit = dtmf_json["DTMF-Digit"]
        if dtmf_digit == "1" and self.__in_talkshow_setup:
            self.request_station_call()
            self.__in_talkshow_setup = False

        elif dtmf_digit == "2" and self.__in_talkshow_setup:#stop the music, put this live on air
            self.hangup_call()  
            self.__in_talkshow_setup = False
 
        elif dtmf_digit == "3":#put the station =in auto_answer
            if self.__phone_status != PhoneStatus.ANSWERING:
                self.__phone_status = PhoneStatus.ANSWERING
                self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'],'/home/amour/media/incoming_auto_answer.mp3')
            else:
                self.__phone_status = PhoneStatus.REJECTING
                self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'], '/home/amour/media/incoming_reject.mp3')

        elif dtmf_digit == "4":#disable auto answer, reject and record all incoming calls
            if self.__phone_status != PhoneStatus.QUEUING:
                self.__phone_status = PhoneStatus.QUEUING
                self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'], '/home/amour/media/incoming_queued.mp3')
            else:
                self.__phone_status = PhoneStatus.REJECTING
                self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'], '/home/amour/media/incoming_reject.mp3')

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

    def notify_host_call(self, call_info):
        #hangup the call
        self.__call_handler.hangup(call_info['Channel-Call-UUID'])
        #reset program
        #self.stop()
        #restart program
        self.start()

    def notify_incoming_call(self, call_info):
        if self.__phone_status == PhoneStatus.ANSWERING: #answer the phone call, join it to the conference
            if len(self.__community_call_UUIDs) == 0:
                self.__call_handler.bridge_incoming_call(call_info['Channel-Call-UUID'], self)
                self.__call_handler.register_for_call_hangup(self, call_info['Caller-Destination-Number'])
                self.__community_call_UUIDs[call_info['Caller-Destination-Number']] = call_info['Channel-Call-UUID']
        elif self.__phone_status == PhoneStatus.QUEUING: #Hangup the phone, call back later
            self.__interested_participants.add(call_info['Caller-ANI'])
            self.__call_handler.play(self.__available_calls[self.__host.phone.raw_number]['Channel-Call-UUID'], '/home/amour/media/incoming_new_caller.mp3')
            print self.__interested_participants
            self.__call_handler.hangup(call_info['Channel-Call-UUID'])

        elif self.__phone_status == PhoneStatus.REJECTING: #Hangup the call
            self.__call_handler.hangup(call_info['Channel-Call-UUID']);
 
    def __schedule_host_callback(self):
        time_delta = timedelta(seconds=600) #one minutes
        now = datetime.utcnow()
        callback_time = now + time_delta
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

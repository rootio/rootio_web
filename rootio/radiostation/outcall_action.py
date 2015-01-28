# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:51:00 PM$"

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime

class OutcallAction:
    
    __argument = None
    start_time = None
    duration = None
    __is_streamed = False
    __warning_time = None
    __radio_station = None
    __scheduler = None
    __call_details = None
    __station_call_available = False 
    __station_call_answer_info = None
    __host_call_answer_info = None
    
    def __init__(self, argument, start_time, duration, is_streamed, warning_time, radio_station):
        self.__argument = argument
        self.start_time = start_time
        self.duration = duration
        self.__is_streamed = is_streamed
        self.__warning_time = warning_time
        self.__radio_station = radio_station
        self.__scheduler = BackgroundScheduler()
        
    def start(self):
        self.__request_call()
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.__hangup_call()
        
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
     
    def __request_call(self):
        raw_result = self.__radio_station.request_call(self, '+256794451574',  'play', self.__argument, self.duration)
        result = raw_result.split(" ")
        print "Result of call is " + str(result)

    def __call_host_number(self): #call the number specified thru plivo
        result = self.__call_details = self.__radio_station.request_call(self, self.__argument, None, None, self.duration) 
        print "result of host call is " + str(result)
    
    def __request_conference_bridge(self, call_UUID, conference_UUID):
        result = self.__radio_station.request_conference(call_UUID, conference_UUID)   
        print result
        #Tell host that they are now live on air?

    def notify_call_answered(self, answer_info):
        if self.__station_call_available == False:#This notification is from answering the station call
            self.__station_call_available = True
            self.__station_call_answer_info = answer_info
            self.__call_host_number() 
        else:#This notification is from answering the host call
            self.__host_call_answer_info = answer_info
            result1 = self.__schedule_warning()
            #print "Result of warning is " + result1
            result2 = self.__schedule_hangup()
            #print "Result of sched hangup is " + result2
            self.__radio_station.request_conference(self.__host_call_answer_info['Channel-Call-UUID'], self.__station_call_answer_info['Channel-Call-UUID'])
            

    def warn_number(self): 
        seconds = self.duration - self.__warning_time
        phrase = "This call will end in %s seconds" % seconds
        print phrase
        #self.__radio_station.speak_to_call(phrase, self.__call_details['CallUUID'])
    
    def __hold_call(self): #put ongoing call on hold
        print "We should be holding now"
    
    def hangup_call(self):  #hangup the ongoing call
        print "We should be hanging up now"
        #self.__radio_station.terminate_call(self.__call_details['CallUUID'])

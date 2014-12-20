# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:51:00 PM$"

from apscheduler.schedulers.background import BackgroundScheduler

class OutCallAction:
    
    __argument = None
    __start_time = None
    __duration = None
    __is_streamed = False
    __warning_time = None
    __radio_station = None
    __scheduler = None
    __call_details = None
    
    
    def __init__(self, argument, start_time, duration, is_streamed, warning_time, radio_station):
        self.__argument = argument
        self.__start_time = start_time
        self.__duration = duration
        self.__is_streamed = is_streamed
        self.__warning_time = warning_time
        self.__radio_station = radio_station
        self.__scheduler = BackgroundScheduler()
        
    def start(self):
        self.__call_number(self.__argument)
        self.__schedule_warning(self.__warning_time)
        self.__schedule_hangup(self.__duration)
    
    def pause(self):
        self.__hold_call()
    
    def stop(self):
        self.__hangup_call()
        
    def __schedule_warning(self):
        time_delta = timedelta(seconds=self.__warning_time)
        now = utcnow()
        warning_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'warn_number'), 'date', None, None, None, 'host_warning', 1, 0, 1, warning_time)
        
    def __schedule_hangup(self):
        time_delta = timedelta(seconds=self.__duration)
        now = utcnow()
        hangup_time = now + time_delta
        self.__scheduler.add_job(getattr(self,'hangup_call'), 'date', None, None, None, 'host_hangup', 1, 0, 1, hangup_time)
     
    def __call_number(self): #call the number specified thru plivo
        self.__call_details = self.__radio_station.request_call(self.__argument, None, None, self.__duration) #fix this
    
    def warn_number(self): 
        seconds = self.__duration - self.__warning_time
        phrase = "This call will end in %s seconds" % seconds
        self.__radio_station.speak_to_call(phrase, self.__call_details['CallUUID'])
    
    def __hold_call(self): #put ongoing call on hold
        pass
    
    def hangup_call(self):  #hangup the ongoing call
        self.__radio_station.terminate_call(self.__call_details['CallUUID'])

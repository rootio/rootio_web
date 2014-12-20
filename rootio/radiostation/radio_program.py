# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:01:00 PM$"

import json
from jingle_action import JingleAction
from media_action import MediaAction
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

class RadioProgram:
    
    __program_actions = []
    __db = None
    __program = None
    __scheduler = None
    __call_queue = []
    __radio_station = None
    __IVR_JSON = None
    __phone_status = PhoneStatus.REJECTING
    
        
    def __init__(self, db, program, radio_station):
        print "initing program with id " + str(program.id)
        self.__db = db
        self.__program = program
        self.__radio_station = radio_station
        self.__scheduler = BackgroundScheduler()
        self.__load_program_actions()
        return
        
    '''
    Starts a station program and does the necessary preparations
    '''
    def start(self):
        self.__schedule_program_actions()
        self.__scheduler.start()
        return
    
    '''
    Load the definition of components of the program from a JSON definition
    '''
    def __load_program_actions(self):
        json_file = open('programactions.json')
        data = json.load(json_file)
        for j in data:
            if j == "Jingle":
                self.__program_actions.append(JingleAction(data["Jingle"]["argument"], data["Jingle"]["start_time"], data["Jingle"]["duration"], data["Jingle"]["is_streamed"], self.__radio_station))
                print "This will start at " + str(data["Jingle"]["start_time"])
                #self.__scheduler.add_job(getattr(program,'start'), 'date', None, None, None, 'scheduled_program', 1, 0, 1, scheduled_program.start))
            if j == "Media":
                self.__program_actions.append(MediaAction(data["Media"]["argument"], data["Media"]["start_time"], data["Media"]["duration"], data["Media"]["is_streamed"], self.__radio_station))
                print "This would have started at " + str(data["Media"]["start_time"])
            if j == "Stream":
                #self.__program_actions.add(JingleAction(j['argument']))
                print "This would have started at " + str(data["Stream"]["start_time"])
            if j == "Music":
                #self.__program_actions.add(MediaAction(j['argument']))
                print "This would have started at " + str(data["Music"]["start_time"])
            if j == "CommunityIVR":
                self.__IVR_JSON = data["CommunityIVR"]
                
        #pprint(data)
        if data["IVR"] != None: #if we have an IVR Menu
            self.__phone_status = PhoneStatus.IVR 
        
        json_file.close
        return
    
    '''
    Schedule the actions of a particular program for playback within the program
    '''
    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            program_action.start()
            #self.__scheduler.add_job(getattr(program_action,'start'), 'date', None, None, None, 'scheduled_program', 1, 0, 1, self.__get_start_datetime(program_action.start_time))
        
    '''
    Get the time at which to schedule the program action to start
    '''        
    def __get_start_datetime(self, time_part):
        t = datetime.strptime(time_part, "%H:%M:%S")
        time_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        print self.__program.start + time_delta
        return self.__program.start + time_delta
    
    '''
    Process an incoming phone call and decide where to route it given the status of the station
    '''
    def handle_call(self, call_info):
        if self.__phone_status == PhoneStatus.REJECTING:
            #hangup the call
            return
        if self.__phone_status == PhoneStatus.QUEUING:
            self.__call_queue.add(call_info["from"])
            self.__call_handler.hangup(call_info["CallUUID"])
            return
        if self.__phone_status == PhoneStatus.AUTOANSWERING:
            #answer the phone call
            return
        if self.__phone_status == PhoneStatus.CONFERENCING:
            #add to the conference call for this show for a defined number of seconds
            return 
        if self.__phone_status == PhoneStatus.IVR:
            ivr_handler = IVR_handler(self.__IVR_JSON,self.__call_handler, call_info['CallUUID'] )
            ivr_handler.handle_IVR(call_info['CallUUID'])
            return 
        if self.__phone_statue == PhoneStatus.RINGING: #Why would anyone want this?
            return
        
        
class PhoneStatus:
    
    REJECTING=1
    QUEUING=2
    AUTOCONFERENCING=3
    CONFERENCING=4
    IVR=5
    RINGING=6
    
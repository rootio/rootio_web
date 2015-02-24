# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:01:00 PM$"

import json
import logging
from outcall_action import OutcallAction
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
    radio_station = None
    __IVR_JSON = None
    __running_action = None
        
    def __init__(self, db, program, radio_station):
        print "initing program with id " + str(program.id)
        logging.basicConfig(filename='rootioweb.log')
        self.__db = db
        self.__program = program
        self.radio_station = radio_station
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
                self.__program_actions.append(JingleAction(data["Jingle"]["argument"], data["Jingle"]["start_time"], data["Jingle"]["duration"], data["Jingle"]["is_streamed"], self))
                print "Jingle scheduled to start at " + str(data["Jingle"]["start_time"])
            if j == "Media":
                self.__program_actions.append(MediaAction(data["Media"]["argument"], data["Media"]["start_time"], data["Media"]["duration"], data["Media"]["is_streamed"], self))
                print "Media Scheduled to start at " + str(data["Media"]["start_time"])
            if j == "Stream":
                #self.__program_actions.add(JingleAction(j['argument']))
                print "Stream would have started at " + str(data["Stream"]["start_time"])
            if j == "Music":
                #self.__program_actions.add(MediaAction(j['argument']))
                print "This would have started at " + str(data["Music"]["start_time"])
            if j == "CommunityIVR":
                self.__IVR_JSON = data["CommunityIVR"]
            if j == "Outcall":
               print "Call to host scheduled to start at " + str(data["Outcall"]["start_time"])
               self.__program_actions.append(OutcallAction(data['Outcall']['argument'],data["Outcall"]["start_time"], data['Outcall']['duration'], data['Outcall']['is_streamed'], data['Outcall']['warning_time'],self) )    
        #pprint(data)
        if data["CommunityIVR"] != None: #if we have an IVR Menu
           pass
 
        json_file.close
        return
    
    '''
    Schedule the actions of a particular program for playback within the program
    '''
    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_job(getattr(program_action,'start'), 'date', None, None, None, str(program_action.start_time), 1, 0, 1, self.__get_start_datetime(program_action.start_time))
         
    def set_running_action(self, running_action):
        if not self.__running_action == None:
            self.__running_action.stop()#clean up any stuff that is not necessary anymore
        self.__running_action = running_action   

    '''
    Get the time at which to schedule the program action to start
    '''        
    def __get_start_datetime(self, time_part):
        t = datetime.strptime(time_part, "%H:%M:%S")
        time_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        print self.__program.start + time_delta
        return self.__program.start + time_delta
    

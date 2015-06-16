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
from interlude_action import InterludeAction
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler

class RadioProgram:
    
    def __init__(self, db, program, radio_station):
        logging.basicConfig(filename='rootioweb.log')
        self.__program_actions = []
        self.id = program.id
        self.__db = db
        self.__program = program
        self.radio_station = radio_station
        self.__scheduler = Scheduler()
        self.__running_action = None
        return
        
    '''
    Starts a station program and does the necessary preparations
    '''
    def start(self):
        self.__load_program_actions()
        self.__schedule_program_actions()
        self.__scheduler.start()
        return
    
    '''
    Load the definition of components of the program from a JSON definition
    '''
    def __load_program_actions(self):
        print self.__program.program.description
        data = json.loads(self.__program.program.description) 
        for j in data:
            if j == "Jingle":
                self.__program_actions.append(JingleAction(data["Jingle"]["argument"], data["Jingle"]["start_time"], data["Jingle"]["duration"], data["Jingle"]["is_streamed"], self))
                print "Jingle scheduled to start at " + str(data["Jingle"]["start_time"])
            if j == "Media":
                self.__program_actions.append(MediaAction(data["Media"]["argument"], data["Media"]["start_time"], data["Media"]["duration"], data["Media"]["is_streamed"], self))
                print "Media Scheduled to start at " + str(data["Media"]["start_time"])
            if j == "Interlude":
                self.__program_actions.append(InterludeAction(data["Interlude"]["argument"], data["Interlude"]["start_time"], data["Interlude"]["duration"], data["Interlude"]["is_streamed"], self))
                print "Interlude Scheduled to start at " + str(data["Interlude"]["start_time"])
            if j == "Stream":
                #self.__program_actions.add(JingleAction(j['argument']))
                print "Stream would have started at " + str(data["Stream"]["start_time"])
            if j == "Music":
                #self.__program_actions.add(MediaAction(j['argument']))
                print "This would have started at " + str(data["Music"]["start_time"])
            if j == "Outcall":
               print "Call to host scheduled to start at " + str(data["Outcall"]["start_time"])
               self.__program_actions.append(OutcallAction(data['Outcall']['argument'],data["Outcall"]["start_time"], data['Outcall']['duration'], data['Outcall']['is_streamed'], data['Outcall']['warning_time'],self) )    
        return
    
    '''
    Schedule the actions of a particular program for playback within the program
    '''
    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_date_job(getattr(program_action,'start'), self.__get_start_datetime(program_action.start_time).replace(tzinfo=None))
         
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
        return self.__program.start + time_delta
    

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:01:00 PM$"

import json
from pprint import pprint
from JingleAction import JingleAction
from MediaAction import MediaAction
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

class RadioProgram:
    
    __program_actions = []
    __db = None
    __program = None
    __scheduler = None
    
        
    def __init__(self, db, program):
        print "initing program with id " + str(program.id)
        self.__db = db
        self.__program = program
        self.__scheduler = BackgroundScheduler()
        self.__load_program_actions()
        
    def start(self):
        self.__schedule_program_actions()
        self.__scheduler.start()
    
    def stop(self):
        pass
    
    def pause(self):
        pass
    
    def __load_program_actions(self):
        json_file = open('programactions.json')
        data = json.load(json_file)
        for j in data:
            if j == "Jingle":
                self.__program_actions.append(JingleAction(data["Jingle"]["argument"], data["Jingle"]["start_time"], data["Jingle"]["duration"]))
                print "This will start at " + str(data["Jingle"]["start_time"])
                #self.__scheduler.add_job(getattr(program,'start'), 'date', None, None, None, 'scheduled_program', 1, 0, 1, scheduled_program.start))
            if j == "Media":
                self.__program_actions.append(MediaAction(data["Media"]["argument"], data["Media"]["start_time"], data["Media"]["duration"]))
                print "This would have started at " + str(data["Media"]["start_time"])
            if j == "Stream":
                #self.__program_actions.add(JingleAction(j['argument']))
                print "This would have started at " + str(data["Stream"]["start_time"])
            if j == "Music":
                #self.__program_actions.add(MediaAction(j['argument']))
                print "This would have started at " + str(data["Music"]["start_time"])
        #pprint(data)
        json_file.close
        return
    
    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_job(getattr(program_action,'start'), 'date', None, None, None, 'scheduled_program', 1, 0, 1, self.__get_start_datetime(program_action._start_time))
    
    def __get_start_datetime(self, time_part):
        t = datetime.strptime(time_part, "%H:%M:%S")
        time_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        print self.__program.start + time_delta
        return self.__program.start + time_delta
        
        
    
    
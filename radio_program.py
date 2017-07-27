# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 20, 2014 3:01:00 PM$"

import dateutil.tz
import json
from advertisement_action import AdvertisementAction
from community_action import CommunityAction
from podcast_action import PodcastAction
from news_action import NewsAction
from outcall_action import OutcallAction
from jingle_action import JingleAction
from media_action import MediaAction
from interlude_action import InterludeAction
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
from rootio_mailer.rootio_mail_message import RootIOMailMessage
from rootio.content.models import ContentTrack

class RadioProgram:
    
    def __init__(self, db, program, radio_station):
        self.__program_actions = []
        self.__status = True
        self.id = program.id
        self.db = db
        self.name = program.id
        self.scheduled_program = program
        self.radio_station = radio_station
        self.__scheduler = Scheduler()
        self.__running_action = None
        self.__rootio_mail_message = RootIOMailMessage()
        return
        
    def start(self):
        self.__load_program_actions()
        self.__run_program_action() #will call the next one when done 
        return
 
    '''
    Load the definition of components of the program from a JSON definition
    '''
    def __load_program_actions(self):
        print self.scheduled_program.program.description
        data = json.loads(self.scheduled_program.program.structure) 
        for action in data:
            if action['type'] == "Advertisements":
                self.__program_actions.insert(0, AdvertisementAction(action["track_id"], action["start_time"], action["duration"], self))
            if action['type'] == "Media":
                self.__program_actions.insert(0, MediaAction(action["track_id"], action["start_time"], action["duration"], self))
            if action['type'] == "Community":
                self.__program_actions.insert(0, CommunityAction(action["category_id"], action["start_time"], action["duration"], self))
            if action['type'] == "Podcast":
                self.__program_actions.insert(0, PodcastAction(action["track_id"], action["start_time"], action["duration"], self))
            if action['type'] == "Music":
                print "This would have started here"
            if action['type'] == "News":
                self.__program_actions.insert(0, NewsAction(action["track_id"], action["start_time"], action["duration"], self))
            if action['type'] == "Outcall":
                self.__program_actions.insert(0, OutcallAction(action['host_id'],action["start_time"], action['duration'], self))    
        return
    
    '''
    Schedule the actions of a particular program for playback within the program
    '''
    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_date_job(getattr(program_action,'start'), self.__get_start_datetime(program_action.start_time).replace(tzinfo=None), misfire_grace_time=program_action.duration)
    
    
    def set_running_action(self, running_action):
        if not self.__running_action == None:
            self.__running_action.stop()#clean up any stuff that is not necessary anymore
        self.__running_action = running_action

    def log_program_activity(self, program_activity):
        self.__rootio_mail_message.append_to_body('%s %s' % (datetime.now().strftime('%y-%m-%d %H:%M:%S'),program_activity))
        pass

    def __run_program_action(self):
       self.__program_actions.pop().start() 
       
    def notify_program_action_stopped(self, played_successfully, call_info): #the next action might need the call.
        self.__status = self.__status and played_successfully
        if len(self.__program_actions) == 0: #all program actions have run
            if call_info != None:
                self.radio_station.call_handler.hangup(call_info['Channel-Call-UUID']) 
            self.__log_program_status()
            self.__send_program_summary()
        else:
            self.__run_program_action()

    def __send_program_summary(self):
        self.__rootio_mail_message.set_subject('[%s] %s ' % (self.radio_station.station.name, self.scheduled_program.program.name))
        self.__rootio_mail_message.set_from('RootIO')#This will come from DB in future
        users = self.__get_network_users()
        for user in users:
            self.__rootio_mail_message.add_to_address(user.email)
        self.__rootio_mail_message.send_message()

    def __log_program_status(self):
        self.db._model_changes = {}
        self.scheduled_program.status = self.__status
        self.radio_station.db.add(self.scheduled_program)
        self.radio_station.db.commit() 

    def __get_network_users(self):
        station_users = self.radio_station.station.network.networkusers
        return station_users
     


    '''
    Get the time at which to schedule the program action to start
    '''        
    def __get_start_datetime(self, time_part):
        now  = datetime.now(dateutil.tz.tzlocal())
        t = datetime.strptime(time_part, "%H:%M:%S")
        time_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return now + time_delta + timedelta(seconds=2) #2 second scheduling allowance
    

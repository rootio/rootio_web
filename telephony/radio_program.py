import json
from datetime import datetime, timedelta

import dateutil.tz
from apscheduler.scheduler import Scheduler
from sqlalchemy.exc import SQLAlchemyError

from advertisement_action import AdvertisementAction
from community_action import CommunityAction
from media_action import MediaAction
from news_action import NewsAction
from outcall_action import OutcallAction
from podcast_action import PodcastAction
from rootio_mailer.rootio_mail_message import RootIOMailMessage


class RadioProgram:

    def __init__(self, program, radio_station):
        self.__rootio_mail_message = RootIOMailMessage()
        self.__program_actions = []
        self.__status = True
        self.id = program.id
        self.name = program.id
        self.scheduled_program = program
        self.radio_station = radio_station
        self.__scheduler = Scheduler()
        self.__running_action = None
        return

    def start(self):
        self.__load_program_actions()
        self.__run_program_action()  # will call the next one when done
        return

    '''
    Load the definition of components of the program from a JSON definition
    '''

    def __load_program_actions(self):
        try:
            data = json.loads(self.scheduled_program.program.structure)
        except ValueError as e:
            print e
            return

        for action in data:
            if "type" in action:
                if action['type'] == "Advertisements":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0, AdvertisementAction(action["track_id"], action["start_time"],
                                                                             action["duration"], self))
                if action['type'] == "Media":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0,
                                                  MediaAction(action["track_id"], action["start_time"],
                                                              action["duration"],
                                                              self))
                if action['type'] == "Community":
                    if "category_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0, CommunityAction(action["category_id"], action["start_time"],
                                                                     action["duration"], self))
                if action['type'] == "Podcast":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0, PodcastAction(action["track_id"], action["start_time"],
                                                                   action["duration"], self))
                if action['type'] == "Music":
                    if "start_time" in action and "duration" in action:
                        self.radio_station.logger.info(
                            "Music program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))

                if action['type'] == "News":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0,
                                                  NewsAction(action["track_id"], action["start_time"],
                                                             action["duration"],
                                                             self))
                if action['type'] == "Outcall":
                    if "host_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0,
                                                  OutcallAction(action['host_id'], action["start_time"],
                                                                action['duration'],
                                                                self))
        return

    '''
    Schedule the actions of a particular program for playback within the program
    '''

    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_date_job(getattr(program_action, 'start'),
                                          self.__get_start_datetime(program_action.start_time).replace(tzinfo=None),
                                          misfire_grace_time=program_action.duration)

    def set_running_action(self, running_action):
        if self.__running_action is not None:
            self.__running_action.stop()  # clean up any stuff that is not necessary anymore
        self.__running_action = running_action

    def log_program_activity(self, program_activity):
        self.__rootio_mail_message.append_to_body(
            '%s %s' % (datetime.now().strftime('%y-%m-%d %H:%M:%S'), program_activity))
        pass

    def __run_program_action(self):
        self.__program_actions.pop().start()

    def notify_program_action_stopped(self, played_successfully, call_info):  # the next action might need the call.
        self.__status = self.__status and played_successfully
        if len(self.__program_actions) == 0:  # all program actions have run
            if call_info is not None and 'Channel-Call-UUID' in call_info:
                self.radio_station.call_handler.hangup(call_info['Channel-Call-UUID'])
            self.__log_program_status()
            self.__send_program_summary()
        else:
            self.__run_program_action()

    def __send_program_summary(self):
        try:
            self.__rootio_mail_message.set_subject(
                '[%s] %s ' % (self.radio_station.station.name, self.scheduled_program.program.name))
            self.__rootio_mail_message.set_from('RootIO')  # This will come from DB in future
            users = self.__get_network_users()
            for user in users:
                self.__rootio_mail_message.add_to_address(user.email)
            self.__rootio_mail_message.send_message()
        except Exception as e:
            self.radio_station.logger.error(e.message)

    def __log_program_status(self):
        try:
            self.radio_station.db._model_changes = {}
            self.scheduled_program.status = self.__status
            self.radio_station.db.add(self.scheduled_program)
            self.radio_station.db.commit()
        except SQLAlchemyError:
            try:
                self.radio_station.db.rollback()
            except:
                return
        except Exception as e:
            self.radio_station.logger.error(e.message)

    def __get_network_users(self):
        station_users = self.radio_station.station.network.networkusers
        return station_users

    '''
    Get the time at which to schedule the program action to start
    '''

    def __get_start_datetime(self, time_part):
        now = datetime.now(dateutil.tz.tzlocal())
        t = datetime.strptime(time_part, "%H:%M:%S")
        time_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return now + time_delta + timedelta(seconds=2)  # 2 second scheduling allowance

import json
import psycopg2
from datetime import datetime, timedelta
from sqlalchemy.pool import NullPool

import dateutil.tz
from apscheduler.scheduler import Scheduler
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from advertisement_action import AdvertisementAction
from community_action import CommunityAction
from media_action import MediaAction
from news_action import NewsAction
from outcall_action import OutcallAction
from podcast_action import PodcastAction
from rootio.config import DefaultConfig
from rootio_mailer.rootio_mail_message import RootIOMailMessage
from .utils.audio import PlayStatus


class RadioProgram:

    def __init__(self, program, radio_station, program_handler):
        self.__rootio_mail_message = RootIOMailMessage()
        self.__program_actions = []
        self.__status = PlayStatus.failed
        self.__call_info = None
        self.id = program.id
        self.name = program.id
        self.__program_handler = program_handler
        self.scheduled_program = program
        self.radio_station = radio_station
        self.__shutting_down = False
        self.__scheduler = Scheduler()
        self.__running_action = None
        return

    def start(self):
        self.__load_program_actions()
        if len(self.__program_actions) == 0:
            return
        else:
            self.__program_handler.set_running_program(self)
            self.__run_program_action()  # will call the next one when done

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
                        self.radio_station.logger.info(
                            "Advertisements program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))

                if action['type'] == "Media":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0,
                                                  MediaAction(action["track_id"], action["start_time"],
                                                              action["duration"],
                                                              self))
                        self.radio_station.logger.info(
                            "Media program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))

                if action['type'] == "Community":
                    if "category_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0, CommunityAction(action["category_id"], action["start_time"],
                                                                     action["duration"], self))
                        self.radio_station.logger.info(
                            "Community program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))
                if action['type'] == "Podcast":
                    if "track_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0, PodcastAction(action["track_id"], action["start_time"],
                                                                   action["duration"], self))
                        self.radio_station.logger.info(
                            "Podcast program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))

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
                        self.radio_station.logger.info(
                            "News program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))

                if action['type'] == "Outcall":
                    if "host_id" in action and "start_time" in action and "duration" in action:
                        self.__program_actions.insert(0,
                                                  OutcallAction(action['host_id'], action["start_time"],
                                                                action['duration'],
                                                                self))
                        self.radio_station.logger.info(
                            "Outcall program scheduled to start at {0} for a duration  {1}".format(action["start_time"],
                                                                                             action["duration"]))
        return

    '''
    Schedule the actions of a particular program for playback within the program
    '''

    def __schedule_program_actions(self):
        for program_action in self.__program_actions:
            self.__scheduler.add_date_job(getattr(program_action, 'start'),
                                          self.__get_start_datetime(program_action.start_time).replace(tzinfo=None),
                                          misfire_grace_time=program_action.duration)

    def stop(self):
        self.__shutting_down = True
        if self.__running_action is not None:
            self.__running_action.stop()

    def set_running_action(self, running_action):
        #if self.__running_action is not None:
        #    self.__running_action.stop()  # clean up any stuff that is not necessary anymore
        self.__running_action = running_action

    def log_program_activity(self, program_activity):
        self.radio_station.logger.info(program_activity)
        self.__rootio_mail_message.append_to_body(
            '%s %s' % (datetime.now().strftime('%y-%m-%d %H:%M:%S'), program_activity))

    def __run_program_action(self):
        if self.__program_actions is not None and len(self.__program_actions) > 0:
            self.radio_station.logger.info("Popping program action from program actions: {0}".format(self.__program_actions))
            self.__program_actions.pop().start()

    def notify_program_action_stopped(self, play_status, call_info):  # the next action might need the call.
        if self.__shutting_down:
            self.radio_station.logger.info("Shutting down this program...")
            self.__status = play_status
            self.radio_station.call_handler.hangup(call_info['Channel-Call-UUID'])
            self.__log_program_status()
        else:
            self.__status = play_status  # For program with multiple actions, if one succeeds then flagged as success!
            if call_info is not None and 'Channel-Call-UUID' in call_info:
                self.__call_info = call_info
            if len(self.__program_actions) == 0:  # all program actions have run
                self.radio_station.logger.info("Program actions array is empty. Program will terminate")

                if self.__call_info is not None:
                    self.radio_station.call_handler.hangup(self.__call_info['Channel-Call-UUID'])
                self.__log_program_status()
                self.__send_program_summary()
            else:
                self.__run_program_action()

    def __send_program_summary(self):
        try:
            self.__rootio_mail_message.set_subject(
                '[%s] %s ' % (self.radio_station.station.name, self.scheduled_program.program.name))
            self.__rootio_mail_message.set_from('info@rootio.org')  # This will come from DB in future
            users = self.__get_network_users()
            for user in users:
                if user.receive_station_notifications:
                    self.__rootio_mail_message.add_to_address(user.email)
            self.__rootio_mail_message.send_message()
        except Exception as e:
            self.radio_station.logger.error("Error {er} in send program summary for {prg}".format(er=str(e),  prg=self.scheduled_program.program.name))

    def __log_program_status(self):
        try:
            conn = psycopg2.connect(DefaultConfig.SQLALCHEMY_DATABASE_URI)
            cur = conn.cursor()
            cur.execute("update radio_scheduledprogram set status = %s where id = %d", (repr(self.__status), self.scheduled_program.id))
            conn.commit()

        except psycopg2.Error as e:
            try:
                self.radio_station.logger.error("Error(1) {err} in radio_program.__log_program_status".format(err=e.message))
            except Exception as e:
                return
        except Exception as e:
            self.radio_station.logger.error("Error(3) {err} in radio_program.__log_program_status".format(err=e.message))
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                self.radio_station.logger.error(
                       "Error(4) {err} in radio_program.__log_program_status".format(err=e.message))

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

import json
import socket
import threading
from time import sleep
from datetime import date, datetime, timedelta, time

import dateutil.tz
import pytz
from pytz import timezone
from apscheduler.scheduler import Scheduler
from rootio.config import DefaultConfig
from rootio.radio.models import ScheduledProgram
from sqlalchemy import text

from radio_program import RadioProgram


class ProgramHandler:

    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__scheduler = None
        self.__scheduled_jobs = None
        self.__start_listeners()
        self.__radio_station.logger.info("Done initialising ProgramHandler for {0}".format(radio_station.station.name))

    def run(self):
        self.run_current_schedule()

    def __prepare_schedule(self):
        self.__load_programs()
        self.__scheduler = Scheduler()
        self.__scheduled_jobs = dict()

    def run_current_schedule(self):
        self.__prepare_schedule()
        self.__scheduler.start()
        self.__schedule_programs()
        self.__schedule_next_schedule()
        print self.__scheduler.get_jobs()

    def stop(self):
        self.__stop_program()
        # any clean up goes here
        # unschedule stuff

    def __schedule_next_schedule(self):
        base_date = datetime.now()
        next_schedule_date = base_date + timedelta(0, 0, 0, 0, 0, 3)  # 3 hours
        self.__scheduler.add_date_job(getattr(self, 'run_current_schedule'), next_schedule_date)

    def __schedule_programs(self):
        for scheduled_program in self.__scheduled_programs:
            if not self.__is_program_expired(scheduled_program):
                self.__add_scheduled_job(scheduled_program)
                self.__radio_station.logger.info(
                    "Scheduled program {0} for station {1} starting at {2}".format(scheduled_program.program.name,
                                                                                   self.__radio_station.station.name,
                                                                                   scheduled_program.start))

    def __add_scheduled_job(self, scheduled_program):
        program = RadioProgram(scheduled_program, self.__radio_station)
        scheduled_job = self.__scheduler.add_date_job(getattr(program, 'start'),
                                                      self.__get_program_start_time(scheduled_program).replace(
                                                          tzinfo=None))
        self.__scheduled_jobs[scheduled_program.id] = scheduled_job

    def __delete_scheduled_job(self, index):
        if not self.__scheduled_jobs:
            self.__radio_station.logger.warning("Failed to delete job (no jobs are scheduled)")
            return

        if index in self.__scheduled_jobs:
            try:
                self.__scheduler.unschedule_job(self.__scheduled_jobs[index])
            except:
                # The job probably ran already
                self.__radio_station.logger.warning("Failed to remove unscheduled job #{}".format(index))
            del self.__scheduled_jobs[index]

    def __stop_program(self):
        # self.__running_program.stop()
        return

    def __run_program(self):
        # self.__running_program.run()
        return

    def __load_programs(self):
        date_filter = "((start >= now() and start < now() + interval '3 hour') or (start < now() and radio_scheduledprogram.end > now()))"
        self.__scheduled_programs = self.__radio_station.db.query(ScheduledProgram).filter(
            ScheduledProgram.station_id == self.__radio_station.station.id).filter(text(date_filter)).filter(
            ScheduledProgram.deleted == False).all()
        self.__radio_station.logger.info("Loaded {1} programs for {0}".format(self.__radio_station.station.name, len(self.__scheduled_programs)))

    def __load_program(self, program_id):
        return self.__radio_station.db.query(ScheduledProgram).filter(ScheduledProgram.id == program_id).first()

    def __start_listeners(self):
        t = threading.Thread(target=self.__listen_for_scheduling_changes,
                             args=(DefaultConfig.SCHEDULE_EVENTS_SERVER_IP, DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))
        t.start()

    def __listen_for_scheduling_changes(self, ip, port):
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (ip, port)

        # It may not be possible to connect after restart, TIME_WAIT could come into play etc. Anyway, keep trying
        connected = False
        while not connected:
            try:
                sck.connect(addr)
                connected = True
            except:
                self.__radio_station.logger.warning(
                    "[Station #{}] Could not connect to server, retrying in 30..."
                    .format(self.__radio_station.id))
                sleep(30)
        sck.send(json.dumps({'station':self.__radio_station.station.id, 'action':'register'}))

        while True:
            data = sck.recv(1024)
            try:
                 event = json.loads(data)
            except ValueError as e:
                 continue
            if "action" in event and "id" in event:
                if event["action"] == "delete":
                    self.__delete_scheduled_job(event["id"])
                    self.__radio_station.logger.info(
                        "Scheduled program with id {0} has been deleted"
                        .format(event["id"]))
                elif event["action"] == "add":
                    scheduled_program = self.__load_program(event["id"])
                    if not self.__is_program_expired(scheduled_program):
                        self.__add_scheduled_job(scheduled_program)
                        self.__radio_station.logger.info(
                            "Scheduled program with id {0} has been added at time {1}"
                            .format(event["id"], scheduled_program.start))
                elif event["action"] == "update":
                    self.__delete_scheduled_job(event["id"])
                    scheduled_program = self.__load_program(event["id"])
                    if not self.__is_program_expired(scheduled_program):
                        self.__add_scheduled_job(scheduled_program)
                        self.__radio_station.logger.info(
                            "Scheduled program with id {0} has been moved to start at time {1}"
                            .format(event["id"], scheduled_program.start))


    """
    Gets the program to run from the current list of programs that are lined up for the day
    """

    def __get_current_program(self):
        for program in self.__scheduled_programs:
            if not self.__is_program_expired(program):
                return program

    """
    Returns whether or not the time for a particular program has passed
    """

    def __is_program_expired(self, scheduled_program):
        now = pytz.utc.localize(datetime.utcnow())
        return (scheduled_program.start + scheduled_program.program.duration) < (now + timedelta(minutes=1))

    def __get_program_start_time(self, scheduled_program):
        now = datetime.now(dateutil.tz.tzlocal())
        if scheduled_program.start < now:  # Time at which program begins is already past
            return now + timedelta(seconds=5)  # 5 second scheduling allowance
        else:
            return scheduled_program.start + timedelta(seconds=5)  # 5 second scheduling allowance

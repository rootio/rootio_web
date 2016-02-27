import datetime
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 2:17:51 PM$"

from rootio.radio.models import ScheduledProgram, Program
from datetime import datetime
from radio_program import RadioProgram
import pytz
from apscheduler.scheduler import Scheduler
from sqlalchemy import text

class ProgramHandler:
    
    def __init__(self, db, radio_station):
        self.__db = db
        self.__radio_station = radio_station
        self.__load_programs()
        self.__scheduler = Scheduler()
        self.__radio_station.logger.info("Done initing ProgramHandler for {0}".format(radio_station.name))
 
    def run(self):
        self.__schedule_programs()
        self.__scheduler.start()
    
    def stop(self):
        self.__stop_program()
        #any clean up goes here
    
    def __schedule_programs(self):
        for scheduled_program in self.__scheduled_programs:#throw all the jobs into AP scheduler and have it rain down alerts
            if not self.__is_program_expired(scheduled_program):
                try:
                    program = RadioProgram(self.__db, scheduled_program, self.__radio_station)
                    self.__scheduler.add_date_job(getattr(program,'start'), scheduled_program.start.replace(tzinfo=None))
                    self.__radio_station.logger.info("Scheduled program {0} for station {1} starting at {2}".format(scheduled_program.program.name, self.__radio_station.name, scheduled_program.start))
                except Exception, e:
                    self.__radio_station.logger.info(str(e))
        return 
    
    def __stop_program(self):
        __running_program.stop()
        return
    
    def __run_program(self):
        __running_program.run()
        return
    
    def __load_programs(self):
        self.__scheduled_programs = self.__db.session.query(ScheduledProgram).filter(ScheduledProgram.station_id == self.__radio_station.id).filter(text("date(start) = current_date")).all()
        self.__radio_station.logger.info("Loaded programs for {0}".format(self.__radio_station.name))
    
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
    def __is_program_expired(self, program):
        original_program = self.__db.session.query(Program).filter(Program.id == program.program_id).one()
        now = pytz.utc.localize(datetime.utcnow())
        return program.start + original_program.duration < now 
    

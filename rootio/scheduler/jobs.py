from messages import start_program
from flask import current_app

from datetime import datetime, timedelta

def schedule_program_start(program_id, station_id, start_time, window=None):
    """Takes a radio.ScheduledProgram and adds it to APScheduler to send message
    within window of program start time."""

    #TEMP do it live
    exec_date = datetime.now() + timedelta(seconds=1)
    #exec_date = start_time - timedelta(seconds=window)

    messenger = current_app.messenger
    #pass zmq while we have access to it
    
    current_app.scheduler.add_date_job(start_program, exec_date, [messenger, program_id, station_id])

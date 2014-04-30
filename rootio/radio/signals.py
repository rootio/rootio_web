from flask.ext.sqlalchemy import models_committed
from models import ScheduledProgram

from ..messenger import messages

@models_committed.connect
def on_models_committed(sender, changes):
    for obj, change in changes:
        print (obj, change)
        if isinstance(obj, ScheduledProgram):
            # don't do any foreignkey lookups here b/c db is in commit
            # just pass id's around, and load them in the job
            print "ScheduledProgram"
            jobs.schedule_program_start(obj.program_id, obj.station_id, obj.start)

        #other models we need to send messages about?
            #station whitelisted numbers

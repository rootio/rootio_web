from flask.ext.sqlalchemy import models_committed
from models import ScheduledProgram

from ..messenger import messages

@models_committed.connect
def on_models_committed(sender, changes):
    for obj, change in changes:
        if isinstance(obj, ScheduledProgram):
            # can't do any foreignkey lookups here b/c db is in commit, just id fields
            # have to load anything else necessary when it hits telephony_server
            messages.schedule_program_start(obj.program_id, obj.station_id, obj.start)

        #other models we need to send messages about?
            # station db fields update (gateway, client_update_frequency, etc)
            # station whitelisted numbers

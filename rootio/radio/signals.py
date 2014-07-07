from flask.ext.sqlalchemy import models_committed
from models import ScheduledProgram, Station

from ..messenger import messages

@models_committed.connect
def on_models_committed(sender, changes):
    """ Check for commits to the database, filtering for models we are interested in
    and send messages to the scheduler or telephony to tell them to deal with it.
    """
    for obj, operation in changes:
        # action will be one of insert, update, delete

        # can't do any foreignkey lookups here b/c db is in commit, just id fields
        # have to load anything else necessary when it hits telephony_server
        if isinstance(obj, ScheduledProgram):
            messages.schedule_program(operation, obj.id, obj.program_id, obj.station_id, obj.start)
        if isinstance(obj, Station) and operation is "update":
            #TODO, determine which fields changed on the model
            #messages.station_update_fields(obj.id, changed_fields)
            pass

        #other models we need to send messages about?
            # station db fields update (gateway, client_update_frequency, etc)
            # station whitelisted numbers

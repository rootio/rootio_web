from flask import current_app

from flask.ext.sqlalchemy import models_committed
from ..radio import ScheduledProgram

def on_program_scheduled(scheduledprogram, change):
    print "scheduled program"
    print scheduledprogram.name
    print change

def on_models_committed(sender, changes):
    print "model commited!"
    for model, change in changes:
        if isinstance(model, ScheduledProgram):
            on_program_scheduled(model, change)

models_committed.connect(on_models_committed, sender=current_app)
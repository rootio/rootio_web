# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, types
from ..extensions import db


class OnAirProgram(db.Model):
    """Repository for actions that occur while the program is on the air.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = "onair_program"
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    scheduledprogram_id = db.Column(db.ForeignKey('radio_scheduledprogram.id'))
    episode_id = db.Column(db.ForeignKey('radio_episode.id'))

    #backrefs
    scheduled_program = db.relationship(u'ScheduledProgram', backref=db.backref('onairprogram',uselist=False))
    # incoming calls and messages
    calls = db.relationship(u'Call', backref=db.backref('onairprogram'))
    messages = db.relationship(u'Message', backref=db.backref('onairprogram'))
    # alternate architectures:
    # increment counters?
    # log in redis?

    def __init__(self):
        #init station, program type, etc thru foreign keys
        self.station = self.scheduled_program.station
        self.program_type = self.scheduled_program.program_type

# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, types
from coaster.sqlalchemy import BaseMixin
from ..extensions import db

class OnAirProgram(BaseMixin, db.Model):
    """Repository for actions that occur while the program is on the air.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = "onair_program"

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

    def __init__(self, scheduled_prog=None, prog_type=None):
        #init station, program type, etc thru foreign keys
	if  (scheduled_prog is None) and (prog_type is None):
        	self.station = self.scheduled_program.station
        	self.program_type = self.scheduled_program.program_type
	elif  scheduled_prog is not None:
		self.scheduled_program = scheduled_prog
		if prog_type is not None:
			self.program_type = prog_type
		else:
			self.program_type = None
	elif  program_type is not None:
		self.program_type = prog_type
		if scheduled_prog is None:
			self.scheduled_program = None

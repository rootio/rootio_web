# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, types
from ..extensions import db


class OnAirEpisode(db.Model):
    """Repository for actions that occur while the episode is on the air.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = "onair_episode"
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    scheduledepisode_id = db.Column(db.ForeignKey('radio_scheduledepisode.id'))

    #backrefs
    scheduled_episode = db.relationship(u'ScheduledEpisode', backref=db.backref('onairepisodes'))
    # incoming calls and messages
    calls = db.relationship(u'Call', backref=db.backref('onairepisode'))
    messages = db.relationship(u'Message', backref=db.backref('onairepisode'))
    # alternate architectures:
    # increment counters?
    # log in redis?

    def __init__(self):
        #init station, program type, etc thru foreign keys
        self.station = self.scheduled_episode.station
        self.program_type = self.scheduled_episode.episode.program.program_type

# -*- coding: utf-8 -*-


from coaster.sqlalchemy import BaseMixin

from ..extensions import db
from ..utils import STRING_LEN

t_meetingstation = db.Table(
    u'governance_meetingstation',
    db.Column(u'meeting_id', db.ForeignKey('governance_meeting.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)


class GovernanceTrack(BaseMixin, db.Model):
    """A track to which audio content is added"""
    __tablename__ = u'governance_meeting'

    meeting_date = db.Column(db.DateTime(), nullable=False)
    minutes = db.Column(db.Text(), nullable=False)
    agenda = db.Column(db.Text(), nullable=False)
    attendees = db.Column(db.Text(), nullable=False)
    track_id = db.Column(db.ForeignKey('content_track.id'))
    creator_id = db.Column(db.ForeignKey('user_user.id'))
    archived = db.Column(db.Boolean, default=False)

    creator = db.relationship(u'User', backref=db.backref('meetings'))
    track = db.relationship(u'ContentTrack', backref=db.backref('meetings'))
    stations = db.relationship(u'Station', secondary=u'governance_meetingstation', backref=db.backref('meetings'))

class OnAirProgram(BaseMixin, db.Model):
    """Repository for actions that occur while the program is on the air.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = "onair_program"

    scheduledprogram_id = db.Column(db.ForeignKey('radio_scheduledprogram.id'))
    episode_id = db.Column(db.ForeignKey('radio_episode.id'))

    # backrefs
    scheduled_program = db.relationship(u'ScheduledProgram', backref=db.backref('onairprogram', uselist=False))
    # incoming calls and messages
    #calls = db.relationship(u'Call', backref=db.backref('onairprogram'))
    messages = db.relationship(u'Message', backref=db.backref('onairprogram'))

    # alternate architectures:
    # increment counters?
    # log in redis?

    def __init__(self):
        # init station, program type, etc thru foreign keys
        self.station = self.scheduled_program.station
        self.program_type = self.scheduled_program.program_type




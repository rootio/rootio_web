from coaster.sqlalchemy import BaseMixin
from sqlalchemy.sql import func

from ..extensions import db
from ..utils import STRING_LEN


class Meeting(BaseMixin, db.Model):
    """
    A meeting concerning one or more stations
    """
    __tablename__ = u'governance_meeting'

    date = db.Column(db.String(STRING_LEN))
    attendees = db.Column(db.String(200))
    agenda = db.Column(db.Boolean)
    minutes = db.Column(db.Integer, default=0)
    archived = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.ForeignKey('user_user.id'))
    track_id = db.Column(db.ForeignKey('content_track.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    track = db.relationship(u'ContentTrack', backref=db.backref('meetings'))


t_stationmeeting = db.Table(
    u'governance_station_meeting',
    db.Column(u'station_id', db.ForeignKey('radio_station.id')),
    db.Column(u'meeting_id', db.ForeignKey('governance_meeting.id'))
)
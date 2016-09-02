from coaster.sqlalchemy import BaseMixin

from ..utils import STRING_LEN
from ..extensions import db
from ..radio import ContentType
from ..user.models import User#, user_user


class ContentTrack(BaseMixin, db.Model):
    "A track record"
    __tablename__ = u'content_track'

    name = db.Column(db.String(STRING_LEN))
    description = db.Column(db.Text)
    uri = db.Column(db.String(200))
    
    content_contenttypeid = db.Column(db.ForeignKey('radio_contenttype.id'))
    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    
    content_type = db.relationship(u'ContentType', backref=db.backref('track_content'))

    def __unicode__(self):
        return self.name


class ContentUploads(BaseMixin, db.Model):
    "A track record"
    __tablename__ = u'content_uploads'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    expiration_date = db.Column(db.DateTime(timezone=True))
    ok_to_play = db.Column(db.Boolean)

    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    contenttrack_id = db.Column(db.ForeignKey('content_track.id'))
    
    content_tracks = db.relationship(u'ContentTrack', backref=db.backref('uploads_track'))

    def __unicode__(self):
        return self.name      
from coaster.sqlalchemy import BaseMixin

from ..utils import STRING_LEN
from ..extensions import db
from ..radio import ContentType
from ..user.models import User#, user_user


class ContentTrack(BaseMixin, db.Model):
    "A track to which audio content is added"
    __tablename__ = u'content_track'

    name = db.Column(db.String(STRING_LEN))
    description = db.Column(db.Text)
    uri = db.Column(db.String(200))
    #add array
    type_id = db.Column(db.ForeignKey('content_type.id'))
    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    
    content_type = db.relationship(u'ContentType', backref=db.backref('track_content'))

    def __unicode__(self):
        return self.name


class ContentUploads(BaseMixin, db.Model):
    "An upload to a particular track"
    __tablename__ = u'content_uploads'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    expiry_date = db.Column(db.DateTime(timezone=True))
    ok_to_play = db.Column(db.Boolean)
    order = db.Column(db.Integer)

    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    track_id = db.Column(db.ForeignKey('content_track.id'))
    type_id = db.Column(db.ForeignKey('content_type.id'))
    
    track = db.relationship(u'ContentTrack', backref=db.backref('track_uploads'))

    def __unicode__(self):
        return self.name      

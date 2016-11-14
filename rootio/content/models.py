from coaster.sqlalchemy import BaseMixin
from sqlalchemy.sql import func
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

class CommunityMenu(BaseMixin, db.Model):
    "An IVR menu for communities to record ads, announcements and greetings"
    __tablename__ = u"content_communitymenu"
 
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    welcome_message = db.Column(db.String(200))
    no_input_message = db.Column(db.String(200))
    days_prompt = db.Column(db.String(200))
    record_prompt = db.Column(db.String(200))
    message_type_prompt = db.Column(db.String(200))
    finalization_prompt = db.Column(db.String(200))
    goodbye_message = db.Column(db.String(200))
    
    station = db.relationship(u'Station', backref=db.backref('community_menu'))
    
class CommunityContent(BaseMixin, db.Model):
    "A message left by a member of the community (ad, greeting, announcement)"
    __tablename__ = u"content_communitycontent"
    
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    originator = db.Column(db.String(20))
    message = db.Column(db.String(100)) 
    duration = db.Column(db.Integer)
    date_created = db.Column(db.DateTime(timezone=True))
    type_code = db.Column(db.Integer)
    valid_until = db.Column(db.DateTime(timezone=True))

    station = db.relationship(u'Station', backref=db.backref('community_content'))

class ContentPodcast(BaseMixin, db.Model):
    "Definition of a podcast"
    __tablename__ = u'content_podcast'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    description = db.Column(db.String(STRING_LEN))
    ok_to_play = db.Column(db.Boolean)
    created_by = db.Column(db.ForeignKey('user_user.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class ContentPodcastDownload(BaseMixin, db.Model):
    "Download of a podcast file"
    __tablename__ = u'content_podcastdownload'

    file_name = db.Column(db.String(STRING_LEN))
    duration = db.Column(db.String(10))
    title = db.Column(db.String(STRING_LEN))
    summary = db.Column(db.String(STRING_LEN))
    podcast_id = db.Column(db.ForeignKey('content_podcast.id'))
    date_downloaded = db.Column(db.DateTime(timezone=True), server_default=func.now())


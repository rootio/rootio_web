# -*- coding: utf-8 -*-

from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.fields.html5 import DateField
from wtforms.validators import Required

from .models import ContentTrack
from ..extensions import db
from ..radio.models import ContentType, Station, Network
from ..user.models import User

ContentTrackFormBase = model_form(ContentTrack, db_session=db.session, base_class=Form,
                                  exclude=['created_at', 'updated_at', 'track_uploads', 'uploaded_by', 'uri'])


class ContentTrackForm(ContentTrackFormBase):
    name = StringField(u'Name', [Required()])
    description = TextAreaField()
    submit = SubmitField(_('Save'))


def all_tracks():
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).all()


def news_tracks():
    content_type = ContentType.query.filter(ContentType.name == 'News').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(
        ContentTrack.type_id == content_type.id).all()


def adds_tracks():
    content_type = ContentType.query.filter(ContentType.name == 'Advertisements').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(
        ContentTrack.type_id == content_type.id).all()


def streams_tracks():
    content_type = ContentType.query.filter(ContentType.name == 'Streams').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(
        ContentTrack.type_id == content_type.id).all()


def musics_tracks():
    content_type = ContentType.query.filter(ContentType.name == 'Media').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(
        ContentTrack.type_id == content_type.id).all()


def stations():
    return Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()


class ContentUploadForm(Form):
    multipart = True
    file = FileField()
    contenttrack_id = QuerySelectField(_('Track name'), query_factory=all_tracks, allow_blank=False)
    submit = SubmitField(_('Save'))


class ContentNewsForm(Form):
    multipart = True
    file = FileField()
    track = QuerySelectField(_('Track name'), [Required()], query_factory=news_tracks, allow_blank=False)
    expiry_date = DateField(_('Expiration Date'))
    submit = SubmitField(_('Save'))


class ContentAddsForm(Form):
    multipart = True
    track = QuerySelectField(_('Track name'), [Required()], query_factory=adds_tracks, allow_blank=False)
    expiry_date = DateField(_('Expiration Date'))
    file = FileField(_('Ad File'))
    submit = SubmitField(_('Save'))


class ContentStreamsForm(Form):
    name = StringField(_('Name of the stream'), [Required()])
    track = QuerySelectField(_('Track name'), [Required()], query_factory=streams_tracks, allow_blank=False)
    uri = StringField(_('URL'))
    expiry_date = DateField(_('Expiration Date'))
    submit = SubmitField(_('Save'))


class ContentMusicForm(Form):
    multipart = True
    track = QuerySelectField(_('Track name'), [Required()], query_factory=musics_tracks, allow_blank=False)
    expiry_date = DateField(_('Expiration Date'))
    file = FileField(_('File(s)'))
    submit = SubmitField(_('Save'))


class CommunityMenuForm(Form):
    multipart = True
    station = QuerySelectField(_('Station'), [Required()], query_factory=stations, allow_blank=False)
    welcome_message = FileField(_('Welcome message'), [Required()])
    days_prompt = FileField(_('Days prompt'), [Required()])
    message_type_prompt = FileField(_('Message type'), [Required()])
    record_prompt = FileField(_('Record Prompt'), [Required()])
    finalization_prompt = FileField(_('Finalization prompt'), [Required()])
    goodbye_message = FileField(_('Goodbye message'), [Required()])
    submit = SubmitField(_('Save'))


class ContentPodcastForm(Form):
    name = StringField(_('Name of the podcast'), [Required()])
    uri = StringField(_('URL'), [Required()])
    description = TextAreaField(_('Description'))
    submit = SubmitField(_('Save'))


class ContentMusicPlaylistForm(Form):
    title = StringField(_('Name of the playlist'), [Required()])
    station = QuerySelectField(_('Station'), [Required()], query_factory=stations, allow_blank=False)
    description = TextAreaField(_('Description'))
    submit = SubmitField(_('Save'))


class ContentStreamForm(Form):
    name = StringField(_('Name of the stream'), [Required()])
    uri = StringField(_('URL'), [Required()])
    description = TextAreaField(_('Description'))
    submit = SubmitField(_('Save'))

# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField#, DateField
#from wtforms.fields import DateField
from wtforms.fields.html5 import DateField
from wtforms import StringField, SelectField, SubmitField, FormField, TextField, TextAreaField, HiddenField, RadioField, IntegerField, FileField

from ..radio.models import ContentType
from .models import ContentTrack, ContentUploads

from ..extensions import db

ContentTrackFormBase = model_form(ContentTrack, db_session=db.session, base_class=Form, exclude=['created_at','updated_at','uploads_track', 'uploaded_by', 'uri'])
class ContentTrackForm(ContentTrackFormBase):
    name = StringField()
    description = TextAreaField()
    submit = SubmitField(_('Save'))

def all_tracks():
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).all()

def news_tracks():
    content_type = ContentType.query.filter(ContentType.name=='News').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(ContentTrack.content_contenttypeid==content_type.id).all() 

def adds_tracks():
    content_type = ContentType.query.filter(ContentType.name=='Adds').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(ContentTrack.content_contenttypeid==content_type.id).all()    

def streams_tracks():
    content_type = ContentType.query.filter(ContentType.name=='Stream').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(ContentTrack.content_contenttypeid==content_type.id).all() 

def musics_tracks():
    content_type = ContentType.query.filter(ContentType.name=='Musics').first()
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).filter(ContentTrack.content_contenttypeid==content_type.id).all()  

class ContentUploadForm(Form): 
    multipart = True
    file = FileField()
    contenttrack_id = QuerySelectField('Track name',query_factory=all_tracks,allow_blank=False)
    submit = SubmitField(_('Save'))


class ContentNewsForm(Form):
    multipart = True 
    file = FileField()
    contenttrack_id = QuerySelectField('Track name',query_factory=news_tracks,allow_blank=False)
    expiration_date = DateField('Expiration Date')
    submit = SubmitField(_('Save'))

class ContentAddsForm(Form):
    multipart = True 
    file = FileField()
    contenttrack_id = QuerySelectField('Track name',query_factory=adds_tracks,allow_blank=False)
    expiration_date = DateField('Expiration Date')
    submit = SubmitField(_('Save'))

class ContentStreamsForm(Form):
    name = StringField('Name of the stream')
    uri = StringField('URL')
    contenttrack_id = QuerySelectField('Track name',query_factory=streams_tracks,allow_blank=False)
    expiration_date = DateField('Expiration Date')
    submit = SubmitField(_('Save'))

class ContentMusicForm(Form):
    multipart = True 
    file = FileField()
    contenttrack_id = QuerySelectField('Track name',query_factory=musics_tracks,allow_blank=False)
    expiration_date = DateField('Expiration Date')
    submit = SubmitField(_('Save'))
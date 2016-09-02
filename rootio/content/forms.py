# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField#, DateField
from wtforms.fields import DateField
#from wtforms.fields.html5 import DateField
from wtforms import StringField, SelectField, SubmitField, FormField, TextField, TextAreaField, HiddenField, RadioField, IntegerField, FileField

from .models import ContentTrack, ContentUploads

from ..extensions import db

ContentTrackFormBase = model_form(ContentTrack, db_session=db.session, base_class=Form, exclude=['created_at','updated_at','uploads_track', 'uploaded_by', 'uri'])
class ContentTrackForm(ContentTrackFormBase):
    name = StringField()
    description = TextAreaField()
    submit = SubmitField(_('Save'))

def all_tracks():
    return ContentTrack.query.filter_by(uploaded_by=current_user.id).all()

ContentUploadFormBase = model_form(ContentUploads, db_session=db.session, base_class=Form, exclude=['created_at','updated_at', 'uri', 'uploaded_by','name'])
class ContentUploadForm(ContentUploadFormBase): 
    file = FileField()
    contenttrack_id = QuerySelectField(query_factory=all_tracks,get_label='name',allow_blank=False)
    #submit = SubmitField(_('Save'))


class ContentNewsForm(ContentUploadFormBase): 
    file = FileField()
    contenttrack_id = QuerySelectField(query_factory=all_tracks,get_label='name',allow_blank=False)
    expiration_date = DateField()
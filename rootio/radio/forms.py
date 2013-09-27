# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SelectField, SubmitField 

from .fields import DurationField
from .models import Station, Program, ProgramType, Person, Language
from .widgets import ChoicesSelect
from .constants import PROGRAM_TYPES, LANGUAGE_CODES

from ..extensions import db

#define field help text here, instead of in model info
StationFormBase = model_form(Station, db_session=db.session, base_class=Form,
    field_args={
        'name':{'description':'Name or callsign of station'},
        'frequency':{'description':'Station broadcast frequency'},
        'phone':{'description': 'Station contact telephone number'},
        'owner':{'description': 'User who is the owner of the station'},
    },
    exclude=[])
class StationForm(StationFormBase):
    submit = SubmitField(u'Save')

def valid_languages():
    return Language.query.all()

def program_types():
    return ProgramType.query.all()

class ProgramForm(Form):
    #can't use model_form, because we want to use a custom field for time duration
    name = StringField(description="") #different syntax here, pass description directly to field constructor
    length = DurationField(description="Duration of the program, in H:MM:SS")
    language = QuerySelectField(query_factory=valid_languages,allow_blank=False)
    program_type = QuerySelectField(query_factory=program_types,allow_blank=False)
    submit = SubmitField(u'Save')


PersonFormBase = model_form(Person, db_session=db.session, base_class=Form)
class PersonForm(PersonFormBase):
    submit = SubmitField(u'Save')

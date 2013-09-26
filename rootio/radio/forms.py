# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form #use wtforms.sqlalchemy model_form to generate fields automatically when we can
from wtforms import StringField, SelectField, SubmitField #and wtforms natively when we can't
from wtforms_components import TimeField #and wtforms_components for fields that wtforms is missing

from .models import Station, Program, Person
from .widgets import ChoicesSelect
from .constants import PROGRAM_TYPES, LANGUAGE_CODES

from ..extensions import db

#define field help text here, instead of in model info
StationFormBase = model_form(Station, db_session=db.session, base_class=Form,
    field_args={
        'name':{'description':'Name or callsign of station'},
        'frequency':{'description':'Station broadcast frequency'},
        'phone':{'description': 'Station contact telephone number'},
        'owner':{'description': 'User who is the owner of the station'}, #render this with a choice widget?
    },
    exclude=[])
class StationForm(StationFormBase):
    submit = SubmitField(u'Save')


class ProgramForm(Form):
    #can't use model_form, because it won't create from wtforms_component TimeField
    name = StringField(description="") #different syntax here, pass description directly to field constructor
    length = TimeField()
    language = SelectField(widget=ChoicesSelect(choices=LANGUAGE_CODES.items())) #TODO: update to read from language objects
    program_type = SelectField(widget=ChoicesSelect(choices=PROGRAM_TYPES.items())) #TODO: update to read from program type objects
    submit = SubmitField(u'Save')

PersonFormBase = model_form(Person, db_session=db.session, base_class=Form)
class PersonForm(PersonFormBase):
    submit = SubmitField(u'Save')

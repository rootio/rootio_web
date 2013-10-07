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

class fixed_choices_field(object):
    field_flags = ('fixed_choices',) #do not display the add-link inline in the admin

#define field help text here, instead of in model info
StationFormBase = model_form(Station, db_session=db.session, base_class=Form,
    field_args={
        'name':{'description':'Name or callsign of station'},
        'frequency':{'description':'Station broadcast frequency'},
        'phone':{'description': 'Station contact telephone number'},
        'owner':{'description': 'User who is the owner of the station','validators':[fixed_choices_field,]},
    },
    exclude=[])
class StationForm(StationFormBase):
    submit = SubmitField(u'Save')


def all_languages():
    return Language.query.all()
def all_program_types():
    return ProgramType.query.all()
class ProgramForm(Form):
    #can't use model_form, because we want to use a custom field for time duration
    name = StringField(description="") #different syntax here, pass description directly to field constructor
    duration = DurationField(description="Duration of the program, in H:MM:SS")
    language = QuerySelectField(query_factory=all_languages,allow_blank=False)
    program_type = QuerySelectField(query_factory=all_program_types,allow_blank=False)
    submit = SubmitField(u'Save')


ProgramTypeFormBase = model_form(ProgramType, db_session=db.session, base_class=Form,
    field_args={
        'definition':{"description":"This field accepts arbitrary Python-dictionaries"},
    })
class ProgramTypeForm(ProgramTypeFormBase):
    submit = SubmitField(u'Save')


PersonFormBase = model_form(Person, db_session=db.session, base_class=Form)
class PersonForm(PersonFormBase):
    submit = SubmitField(u'Save')


LanguageFormBase = model_form(Language, db_session=db.session, base_class=Form,
    only=['name','iso639_1','iso639_2','locale_code'],) #explicitly include only these fields, so we don't have to exclude m2m fks
class LanguageForm(LanguageFormBase):
    submit = SubmitField(u'Save')

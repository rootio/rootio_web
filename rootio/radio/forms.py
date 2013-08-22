# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import HiddenField, SubmitField
from wtforms_alchemy import ModelForm
from .models import Station, Program, Person

class StationForm(ModelForm, Form):
    class Meta:
        model = Station
    submit = SubmitField(u'Save')


class ProgramForm(ModelForm, Form):
    class Meta:
        model = Program
    submit = SubmitField(u'Save')


class PersonForm(ModelForm, Form):
    class Meta:
        model = Person
    submit = SubmitField(u'Save')


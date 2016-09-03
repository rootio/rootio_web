from flask.ext.wtf import Form, validators
from flask.ext.babel import gettext as _
from flask import flash
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SelectField, SubmitField, FormField, TextField, TextAreaField, HiddenField, RadioField, IntegerField, DateTimeField
from wtforms_components.fields import TimeField
from wtforms.validators import Required, AnyOf
import pytz


from .models import ChatBotCmd
from ..radio.models import BotFunctions

from ..extensions import db




AddBotFunctionFormBase = model_form(BotFunctions, db_session=db.session, base_class=Form,
    field_args={ 'name':{'description':_('Name of the functions that the bot will execute')}})
class AddBotFunction(AddBotFunctionFormBase):
    submit = SubmitField(_('Save'))


AddNewCommandFormBase =  model_form(ChatBotCmd, db_session=db.session, base_class=Form)
class AddNewCommand(AddNewCommandFormBase):
    submit = SubmitField(_('Save'))

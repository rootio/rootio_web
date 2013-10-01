from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import SubmitField 

from .models import PhoneNumber
from ..extensions import db

PhoneNumberFormBase = model_form(PhoneNumber, db_session=db.session, base_class=Form)
class PhoneNumberForm(PhoneNumberFormBase):
    submit = SubmitField(u'Save')
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import SubmitField, RadioField
from wtforms.validators import AnyOf

from .constants import PHONE_NUMBER_TYPE

from .models import PhoneNumber
from ..extensions import db

PhoneNumberFormBase = model_form(PhoneNumber, db_session=db.session, base_class=Form,
    exclude=['areacode',])
class PhoneNumberForm(PhoneNumberFormBase):
    number_type = RadioField(u"Type", [AnyOf([str(val) for val in PHONE_NUMBER_TYPE.keys()])],
            choices=[(str(val), label) for val, label in PHONE_NUMBER_TYPE.items()])
    submit = SubmitField(u'Save')
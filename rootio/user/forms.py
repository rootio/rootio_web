# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, TextField,
        PasswordField, SubmitField, SelectMultipleField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField)

from wtforms.validators import (ValidationError, AnyOf, Optional,
        Required, Length, EqualTo, Email, NumberRange, URL)
from flask_wtf.html5 import DateField, URLField, EmailField, TelField
from flask.ext.login import current_user
from rootio.radio.models import Network

from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import model_form
from ..user import RootioUser, User
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX
from ..utils import allowed_file, ALLOWED_AVATAR_EXTENSIONS
from ..utils import GENDER_TYPE
from ..extensions import db

from .constants import USER_ROLE, USER_STATUS


class UserForm(Form):
    next = HiddenField()
    role_code = RadioField(_("Role"), [AnyOf([str(val) for val in USER_ROLE.keys()])],
            choices=[(str(val), label) for val, label in USER_ROLE.items()])
    status_code = RadioField(_("Status"), [AnyOf([str(val) for val in USER_STATUS.keys()])],
            choices=[(str(val), label) for val, label in USER_STATUS.items()])
    # A demo of datepicker.
    created_time = DateField(_('Created time'))
    submit = SubmitField(_('Save'))

ProfileCreateFormBase = model_form(RootioUser, db_session=db.session, base_class=Form, exclude=['created_time','avatar','user_detail_id','openid','activation_key','last_accessed','status_code'])
class ProfileCreateForm(ProfileCreateFormBase):
    multipart = True
    next = HiddenField()
    networks = QuerySelectMultipleField(query_factory=lambda: current_user.networks) #netwoks = (current_user.name,[Required()])
    email = EmailField(u'Email', [Required(), Email()])
    name = TextField(u'Name', [Required(), Length(max=100)])
    password = PasswordField(u'Password', [Required(), Length(max=100)])
    password1 = PasswordField(u'Retype-password', [Required(), Length(max=100)])
    role_code = RadioField(_("Role"), [AnyOf([str(val) for val in USER_ROLE.keys()])], choices=[(str(val), label) for val, label in USER_ROLE.items()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(u"Avatar", [Optional()])
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])], choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(u'Age', [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(u'Phone', [Length(max=64)])
    url = URLField(u'URL', [Optional(), URL()])
    location = TextField(u'Location', [Length(max=64)])
    bio = TextAreaField(u'Bio', [Length(max=1024)])
    submit = SubmitField(u'Save')

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))

    def validate_password(self, field):
        if field.data != self.password1.data:
            raise ValidationError("The Passwords Don't Match")

ProfileFormBase = model_form(RootioUser, db_session=db.session, base_class=Form, exclude=['created_time','avatar','user_detail_id','openid','activation_key','last_accessed','status_code'])
class ProfileForm(ProfileFormBase):
    multipart = True
    next = HiddenField()
    name = TextField(u'Name', [Required()])
    email = EmailField(u'Email', [Required(), Email()])
    role_code = RadioField(u"Role", choices=[])
    #role_code = RadioField(_("Role")) #, [AnyOf([str(val) for val in USER_ROLE.keys()])], choices=[(str(val), label) for val, label in role_codes().items()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(u"Avatar", [Optional()])
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])], choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(u'Age', [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(u'Phone', [Length(max=64)])
    url = URLField(u'URL', [Optional(), URL()])
    location = TextField(u'Location', [Length(max=64)])
    bio = TextAreaField(u'Bio', [Length(max=1024)])
    submit = SubmitField(u'Save')

    def get_role_codes(self, role_code):
        if role_code == 0:
            roles = USER_ROLE
        elif role_code == 3:
            roles = {k: v for k, v in USER_ROLE.items() if k in ('2','3')}
        elif role_code == 1:
            roles = USER_ROLE[1:2]
        self.role_code = RadioField(_("Role"), [AnyOf([str(val) for val in roles.keys()])], choices=[(str(val), label) for val, label in roles.items()])


    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))



class EditProfileForm(Form):
    multipart = True
    next = HiddenField()
    networks = QuerySelectMultipleField(query_factory=lambda: current_user.networks)
    email = EmailField(u'Email', [Required(), Email()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(u"Avatar", [Optional()])
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])], choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(u'Age', [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(u'Phone', [Length(max=64)])
    url = URLField(u'URL', [Optional(), URL()])
    location = TextField(u'Location', [Length(max=64)])
    bio = TextAreaField(u'Bio', [Length(max=1024)])
    submit = SubmitField(u'Save')
    
    def set_networks(self, networks):
        #self.networks.choices = networks
        pass

    def validate_name(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_name(field.data):
            raise ValidationError("Please pick another name.")

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))

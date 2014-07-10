# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import (HiddenField, TextField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, SelectField)
from wtforms.validators import (ValidationError, AnyOf, Optional,
        Required, Length, EqualTo, Email, NumberRange, URL)
from flask_wtf.html5 import URLField, EmailField, TelField
from flask.ext.login import current_user

from ..user import User
from ..user.constants import USER_ROLE, USER_STATUS
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX
from ..utils import allowed_file, ALLOWED_AVATAR_EXTENSIONS
from ..utils import GENDER_TYPE


class ProfileForm(Form):
    multipart = True
    next = HiddenField()
    email = EmailField(u'Email', [Required(), Email()])
    role_code = SelectField(u'Role', choices=USER_ROLE.items(), coerce=int)
    status_code = SelectField(u'Status', choices=USER_STATUS.items(), coerce=int)
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(u"Avatar", [Optional()])
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])], choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(u'Age', [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(u'Phone', [Length(max=64)])
    url = URLField(u'URL', [Optional(), URL()])
    location = TextField(u'Location', [Length(max=64)])
    bio = TextAreaField(u'Bio', [Length(max=1024)])
    submit = SubmitField(u'Save')

    def validate_name(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_name(field.data):
            raise ValidationError("Please pick another name.")

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))


class ProfileCreateForm(Form):
    multipart = True
    next = HiddenField()
    email = EmailField(u'Email', [Required(), Email()])
    name = TextField(u'Name', [Required(), Length(max=100)])
    role_code = SelectField(u'Role', choices=USER_ROLE.items(), coerce=int)
    status_code = SelectField(u'Status', choices=USER_STATUS.items(), coerce=int)
    password = PasswordField(u'Password', [Required(), Length(max=100)])
    password1 = PasswordField(u'Retype-password', [Required(), Length(max=100)])
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


class PasswordForm(Form):
    next = HiddenField()
    password = PasswordField('Current password', [Required()])
    new_password = PasswordField('New password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField('Password again', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('new_password')])
    submit = SubmitField(u'Save')

    def validate_password(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_password(field.data):
            raise ValidationError("Password is wrong.")

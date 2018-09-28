# -*- coding: utf-8 -*-

from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from flask.ext.wtf import Form
from flask_wtf.html5 import URLField, EmailField, TelField
from wtforms import (HiddenField, TextField,
                     PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
                     FileField)
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import (ValidationError, AnyOf, Optional,
                                Required, Length, EqualTo, Email, NumberRange, URL)

from ..user import User
from ..utils import GENDER_TYPE
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX
from ..utils import allowed_file, ALLOWED_AVATAR_EXTENSIONS


class ProfileForm(Form):
    multipart = True
    next = HiddenField()
    email = EmailField(_('Email'), [Required(), Email()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(_("Avatar"), [Optional()])
    gender_code = RadioField(_("Gender"), [AnyOf([str(val) for val in GENDER_TYPE.keys()])],
                             choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(_('Age'), [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(_('Phone'), [Length(max=64)])
    url = URLField(_('URL'), [Optional(), URL()])
    location = TextField(_('Location'), [Length(max=64)])
    bio = TextAreaField(_('Bio'), [Length(max=1024)])
    submit = SubmitField(_('Save'))

    def validate_name(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_name(field.data):
            raise ValidationError(_("Please pick another name."))

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError(_("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS)))


class ProfileCreateForm(Form):
    multipart = True
    next = HiddenField()
    networks = QuerySelectMultipleField(
        query_factory=lambda: current_user.networks) # networks = (current_user.name,[Required()])
    email = EmailField(_('Email'), [Required(), Email()])
    name = TextField(_('Name'), [Required(), Length(max=100)])
    password = PasswordField(_('Password'), [Required(), Length(max=100)])
    password1 = PasswordField(_('Retype-password'), [Required(), Length(max=100)])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(_("Avatar"), [Optional()])
    gender_code = RadioField(_("Gender"), [AnyOf([str(val) for val in GENDER_TYPE.keys()])],
                             choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    age = IntegerField(_('Age'), [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(_('Phone'), [Length(max=64)])
    url = URLField(_('URL'), [Optional(), URL()])
    location = TextField(_('Location'), [Length(max=64)])
    bio = TextAreaField(_('Bio'), [Length(max=1024)])
    submit = SubmitField(_('Save'))

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError(_("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS)))

    def validate_password(self, field):
        if field.data != self.password1.data:
            raise ValidationError(_("The Passwords Don't Match"))


class PasswordForm(Form):
    next = HiddenField()
    password = PasswordField(_('Current password'), [Required()])
    new_password = PasswordField(_('New password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField(_('Password again'),
                                   [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('new_password')])
    submit = SubmitField(_('Save'))

    def validate_password(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_password(field.data):
            raise ValidationError(_("Password is wrong."))

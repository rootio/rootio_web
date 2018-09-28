# -*- coding: utf-8 -*-

from flask import Markup

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, BooleanField, TextField,
                     PasswordField, SubmitField)
from wtforms.validators import ValidationError, Required, Length, EqualTo, Email
from flask_wtf.html5 import EmailField

from ..user import User
from ..utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
                     USERNAME_LEN_MIN, USERNAME_LEN_MAX)


class LoginForm(Form):
    next = HiddenField()
    login = TextField(_('Username or email'), [Required()])
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField(_('Remember me'))
    submit = SubmitField(_('Sign in'))


class SignupForm(Form):
    next = HiddenField()
    email = EmailField(_('Email'), [Required(), Email()],
                       description=_("What's your email address?"))
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
                             description=_('%s characters or more' % PASSWORD_LEN_MIN))
    name = TextField(_('Choose your username'), [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
                     description=_("Don't worry. you can change it later."))
    agree = BooleanField(Markup(_('Agree to the <a target="blank" href="/terms">Terms of Service</a>')), [Required()])
    submit = SubmitField(_('Sign up'))

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This username is already registered'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_('This email is already registered'))


class RecoverPasswordForm(Form):
    email = EmailField(_('Your email'), [Email()])
    submit = SubmitField(_('Send instructions'))


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    email = HiddenField()
    password = PasswordField(_('Password'), [Required()])
    password_again = PasswordField(_('Password again'), [EqualTo('password', message=_('Passwords don\'t match'))])
    submit = SubmitField(_('Save'))


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField(_('Reauthenticate'))


class OpenIDForm(Form):
    openid = TextField(_('Your OpenID'), [Required()])
    submit = SubmitField(_('Log in with OpenID'))


class CreateProfileForm(Form):
    openid = HiddenField()
    name = TextField(_('Choose your username'), [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=_('Don\'t worry. you can change it later.'))
    email = EmailField(_('Email'), [Required(), Email()], description=_('What\'s your email address?'))
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=_('%s characters or more! Be tricky.' % PASSWORD_LEN_MIN))
    submit = SubmitField(_('Create Profile'))

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This username is taken.'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_('This email is taken.'))

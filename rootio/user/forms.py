# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import HiddenField, SubmitField, RadioField, DateField
from wtforms.validators import AnyOf

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

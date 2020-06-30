# -*- coding: utf-8 -*-

from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.fields.html5 import DateTimeField, DateField
from wtforms.validators import Required

from rootio.content import ContentTrack
from rootio.user import ADMIN
from ..extensions import db
from ..onair import GovernanceMeeting
from ..radio.models import Station, Network

GovernanceMeetingFormBase = model_form(GovernanceMeeting, db_session=db.session, base_class=Form,
                                  exclude=['created_at', 'updated_at', 'stations', 'creator', 'track', 'archived'])


def user_tracks():
    if current_user.role_code == ADMIN:
        networks = Network.query.all()
    else:
        networks = current_user.networks
    network_ids = [network.id for network in networks]
    tracks = db.session.query(ContentTrack).join(ContentTrack.networks).filter(ContentTrack.deleted != True).filter(
        Network.id.in_(network_ids))
    return tracks


def stations():
    return Station.get_stations(current_user)


class GovernanceMeetingForm(GovernanceMeetingFormBase):
    meeting_date = DateField(_('Meeting date'), [Required()], format='%Y-%m-%d')
    attendees = TextAreaField(_('Attendees'), [Required()])
    agenda = TextAreaField(_('Agenda'), [Required()])
    minutes = TextAreaField(_('Minutes'), [Required()])
    stations = QuerySelectMultipleField('Stations', [Required()], query_factory=stations, allow_blank=False)
    track = QuerySelectField(_('Track name'), [Required()], query_factory=user_tracks, allow_blank=True, blank_text=_('--Select--'))
    submit = SubmitField(_('Save'))



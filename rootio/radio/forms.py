# -*- coding: utf-8 -*-

import pytz
from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, \
    TextField, TextAreaField, HiddenField, RadioField, \
    IntegerField, FloatField, DecimalField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import Required, AnyOf, NumberRange
from wtforms_components.fields import TimeField


from .fields import DurationField, InlineFormField, JSONField
from .models import Station, Network, Program, ProgramType, ScheduledBlock, Person, Language, Location, ContentType, \
    TtsVoice, TtsAudioFormat, TtsSampleRate
from .validators import HasInlineForm
from ..extensions import db
from ..telephony.forms import PhoneNumberForm
from ..user.models import User
from ..utils import OrderedForm, GENDER_TYPE

LocationFormBase = model_form(Location, db_session=db.session, base_class=Form,
                              field_args={'latitude': {'description': '+N / -S'},
                                          'longitude': {'description': '+E / -W'}},
                              exclude=['created_at', 'updated_at'])


class LocationForm(LocationFormBase):
    submit = SubmitField(_('Save'))


def all_networks():
    return Network.query.join(User, Network.networkusers).filter(User.id == current_user.id).all()


# define field help text here, instead of in model info
StationFormBase = model_form(Station, db_session=db.session, base_class=OrderedForm,
                             field_args={
                                 'name': {'description': _('Name or callsign of station')},
                                 'frequency': {'description': _('Station broadcast frequency')},
                                 'location': {'validators': [HasInlineForm, ]},
                                 'phone': {'description': _('Station contact telephone number'),
                                           'validators': [HasInlineForm, ]},
                                 'languages': {'description': _("Primary languages the station will broadcast in")},
                                 'client_update_frequency': {'description': _(
                                     "How frequently the transmitter should check for updates, in seconds")},
                                 'broadcast_ip': {'description': _(
                                     "IP address of the transmitter on the local network. Should start with 230.")},
                             },
                             exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics', 'owner',
                                      'loop_ads', 'loop_greetings', 'loop_announcements',
                                      'whitelist_number', 'outgoing_gateways', 'incoming_gateways',
                                      'primary_transmitter_phone_id', 'primary_transmitter_phone',
                                      'client_update_frequency', 'analytic_update_frequency', 'broadcast_ip',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'tts_voice', 'tts_samplerate','tts_audioformat', 'call_volume', 'audio_volume',
                                      'secondary_transmitter_phone_id', 'secondary_transmitter_phone', 'community_menu',
                                      'community_content', 'music', 'albums', 'playlists', 'artists', 'broadcast_ip',
                                               'broadcast_port', 'last_accessed_mobile', 'tts_language',
                                      'is_high_bandwidth', 'sip_username', 'sip_password', 'sip_server',
                                      'sip_port','sip_stun_server', 'sip_reregister_period', 'sip_protocol', 'media_amplification_factor', 'jingle_interval',
                                      'events'])


def all_languages():
    return Language.query.all()


class StationForm(StationFormBase):
    name = TextField(_('Station Name'), [Required()])
    network = QuerySelectField(u'Network', [Required()], query_factory=all_networks, allow_blank=False)
    phone_inline = InlineFormField(PhoneNumberForm, description='/telephony/phonenumber/add/ajax/')
    languages = QuerySelectMultipleField(_('Languages'), [Required()], query_factory=all_languages)
    api_key = TextField(_('Key for communication with the API'), [Required()])
    timezone = SelectField(choices=[(val, val) for val in pytz.common_timezones], default="UTC")
    frequency = FloatField(_('Broadcasting Frequency'))
    about = TextAreaField(_('About the station'))
    # inline form and POST url for phone creation modal
    # ugly overloading of the description field. WTForms won't let us attach any old random kwargs...
    location_inline = InlineFormField(LocationForm, description='/radio/location/add/ajax/')
    submit = SubmitField(_('Save'))
    field_order = ('network', 'name', 'location', 'timezone',  '*')





def all_program_types():
    return ProgramType.query.all()


class ProgramForm(Form):
    # can't use model_form, because we want to use a custom field for time duration
    name = StringField()
    description = TextAreaField()
    program_structure = TextAreaField(description=_("Drag content here in desired order, double click to reset"))
    structure = TextAreaField(u'')
    duration = DurationField(_("Duration of the program, in HH:MM(:SS)"),[Required()])
    # language = QuerySelectField(query_factory=all_languages,allow_blank=False)
    # program_type = QuerySelectField(query_factory=all_program_types,allow_blank=False)
    networks = QuerySelectMultipleField(_('Networks'), [Required()], query_factory=all_networks)
    submit = SubmitField(_('Save'))


ProgramTypeFormBase = model_form(ProgramType, db_session=db.session, base_class=Form,
                                 field_args={
                                     'definition': {"description": _("This field expects JSON")},
                                     'phone_functions': {"description": _("This field expects JSON")},
                                 }, exclude=['created_at', 'updated_at'])


class ProgramTypeForm(ProgramTypeFormBase):
    definition = JSONField()
    phone_functions = JSONField()
    submit = SubmitField(_('Save'))


ContentTypeFormBase = model_form(ContentType, db_session=db.session, base_class=Form,
                                 exclude=['created_at', 'updated_at'])


class ContentTypeForm(ContentTypeFormBase):
    name = StringField()
    description = TextAreaField()
    submit = SubmitField(_('Save'))


NetworkFormBase = model_form(Network, db_session=db.session, base_class=Form,
                             exclude=['people', 'networkusers', 'stations', 'created_at', 'paddingcontents',
                                      'updated_at','programs'])


class NetworkForm(NetworkFormBase):
    name = TextField(u'Name', [Required()])
    about = TextAreaField()
    submit = SubmitField(_('Save'))


PersonFormBase = model_form(Person, db_session=db.session, base_class=Form,
                            exclude=['deleted'],
                            field_args={'phone': {'validators': [HasInlineForm, ]}})


class PersonForm(PersonFormBase):
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])],
                             choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    phone_inline = InlineFormField(PhoneNumberForm, description='/telephony/phonenumber/add/ajax/')
    networks = QuerySelectMultipleField('Networks', [Required()], query_factory=all_networks)
    submit = SubmitField(_('Save'))


LanguageFormBase = model_form(Language, db_session=db.session, base_class=Form,
                              only=['name', 'iso639_1', 'iso639_2',
                                    'locale_code'], )  # explicitly include only these fields,
#  so we don't have to exclude m2m fks


class LanguageForm(LanguageFormBase):
    submit = SubmitField(_('Save'))


def all_stations():
    return Station.query.all()


class BlockForm(Form):
    name = StringField()
    station = QuerySelectField(query_factory=all_stations, allow_blank=False)
    start_time = TimeField()
    end_time = TimeField()
    recurrence = HiddenField()
    submit = SubmitField(_('Save'))


def all_programs():
    return Program.query.all()


def all_blocks():
    return ScheduledBlock.query.all()


class ScheduleProgramForm(Form):
    # station = QuerySelectField(query_factory=all_stations,allow_blank=False)
    station = TextField(u'Station')
    program = QuerySelectField(query_factory=all_programs, allow_blank=True, blank_text='- select program -')
    # block = QuerySelectField(query_factory=all_blocks,allow_blank=False) #let user select block?
    air_time = TimeField(u'')
    recurrence = HiddenField()
    # priority = IntegerField(description=_("Ascending values"))
    # other options for flexibility?
    submit = SubmitField(_('Save'))


WhitlistsFormBase = model_form(Person, db_session=db.session, base_class=Form)


class WhitlistsForm(WhitlistsFormBase):
    submit = SubmitField(_('Save'))

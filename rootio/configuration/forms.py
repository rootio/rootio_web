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


from ..radio.fields import DurationField, InlineFormField, JSONField
from ..radio.models import Station, Network, Program, ProgramType, ScheduledBlock, Person, Language, Location, ContentType, \
    TtsVoice, TtsAudioFormat, TtsSampleRate
from ..radio.validators import HasInlineForm
from ..extensions import db
from ..telephony.forms import PhoneNumberForm
from ..user.models import User
from ..utils import OrderedForm, GENDER_TYPE

StationTelephonyFormBase = model_form(Station, db_session=db.session, base_class=Form,
                                      field_args={
                                          'primary_transmitter_phone': {'validators': [HasInlineForm, ]},
                                          'secondary_transmitter_phone': {'validators': [HasInlineForm, ]}},
                                      exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics',
                                               'name', 'about', 'frequency', 'api_key', 'timezone', 'owner_id',
                                               'location_id', 'owner', 'location', 'languages',
                                               'client_update_frequency', 'analytic_update_frequency', 'broadcast_ip', 'jingle_interval',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'tts_voice', 'tts_samplerate','tts_audioformat','call_volume', 'audio_volume', 'sip_username',
                                               'sip_password', 'sip_server', 'sip_port', 'sip_stun_server',
                                               'sip_reregister_period', 'sip_protocol', 'media_amplification_factor','is_high_bandwidth', 'events'])


class StationTelephonyForm(StationTelephonyFormBase):
    primary_transmitter_phone_inline = InlineFormField(PhoneNumberForm, description='/telephony/phonenumber/add/ajax/')
    secondary_transmitter_phone_inline = InlineFormField(PhoneNumberForm,
                                                     description='/telephony/phonenumber/add/ajax/')
    submit = SubmitField(_('Save'))


StationSipTelephonyFormBase = model_form(Station, db_session=db.session, base_class=Form,
                                      field_args={
                                          'primary_transmitter_phone': {'validators': [HasInlineForm, ]},
                                          'secondary_transmitter_phone': {'validators': [HasInlineForm, ]}},
                                      exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics',
                                               'name', 'about', 'frequency', 'api_key', 'timezone', 'owner_id',
                                               'location_id', 'owner', 'location', 'languages',
                                               'client_update_frequency', 'analytic_update_frequency', 'broadcast_ip', 'jingle_interval',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'tts_voice', 'tts_samplerate','tts_audioformat','call_volume', 'audio_volume', 'scheduled_programs',
                                               'blocks', 'created_at', 'updated_at', 'analytics', 'owner', 'events',
                                      'whitelist_number', 'outgoing_gateways', 'incoming_gateways',
                                      'primary_transmitter_phone_id', 'primary_transmitter_phone',
                                      'secondary_transmitter_phone_id', 'secondary_transmitter_phone', 'community_menu',
                                      'community_content', 'music', 'albums', 'playlists', 'artists', 'broadcast_ip',
                                               'broadcast_port', 'last_accessed_mobile', 'tts_language', 'media_amplification_factor'])


class StationSipTelephonyForm(StationSipTelephonyFormBase):
    sip_protocol = SelectField(choices=[(val, val) for val in ["udp", "tcp"]])
    sip_port = IntegerField(_('SIP Port'), [NumberRange(1, 65535, _('1 - 65535'))])
    sip_reregister_period = IntegerField(_('Re-register Period'), [NumberRange(30, 3600, _('30 - 3600'))])
    submit = SubmitField(_('Save'))


StationAudioLevelsFormBase = model_form(Station, db_session=db.session, base_class=Form,
                                      field_args={
                                          'primary_transmitter_phone': {'validators': [HasInlineForm, ]},
                                          'secondary_transmitter_phone': {'validators': [HasInlineForm, ]}},
                                      exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics',
                                               'name', 'about', 'frequency', 'api_key', 'timezone', 'owner_id',
                                               'location_id', 'owner', 'location', 'languages',
                                               'broadcast_ip',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'tts_voice', 'tts_samplerate','tts_audioformat',
                                               'scheduled_programs','client_update_frequency', 'analytic_update_frequency',
                                               'blocks', 'created_at', 'updated_at', 'analytics', 'owner', 'events',
                                      'whitelist_number', 'outgoing_gateways', 'incoming_gateways',
                                      'primary_transmitter_phone_id', 'primary_transmitter_phone','call_volume', 'audio_volume',
                                      'secondary_transmitter_phone_id', 'secondary_transmitter_phone', 'community_menu',
                                      'community_content', 'music', 'albums', 'playlists', 'artists', 'broadcast_ip',
                                               'broadcast_port', 'last_accessed_mobile', 'tts_language', 'sip_username',
                                               'sip_password', 'sip_server', 'sip_port', 'sip_stun_server',
                                               'sip_reregister_period', 'sip_protocol', 'is_high_bandwidth',
                                               'media_amplification_factor'])


class StationAudioLevelsForm(StationAudioLevelsFormBase):
    audio_volume = SelectField(choices=[(str(val), str(val)) for val in range(1, 15, 1)], default="8")
    call_volume = SelectField(choices=[(str(val), str(val)) for val in range(1, 6, 1)], default="6")
    media_amplification_factor = SelectField(choices=[(str(val), str(val)) for val in range(0, 3, 1)], default="0")
    jingle_interval = IntegerField(_('Jingle play interval'), [NumberRange(1, 1440, _('1 - 1440'))])
    submit = SubmitField(_('Save'))


StationSynchronizationFormBase = model_form(Station, db_session=db.session, base_class=Form,
                                      field_args={
                                          'primary_transmitter_phone': {'validators': [HasInlineForm, ]},
                                          'secondary_transmitter_phone': {'validators': [HasInlineForm, ]}},
                                      exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics',
                                               'name', 'about', 'frequency', 'api_key', 'timezone', 'owner_id',
                                               'location_id', 'owner', 'location', 'languages',
                                               'client_update_frequency', 'analytic_update_frequency', 'broadcast_ip',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'scheduled_programs','client_update_frequency', 'analytic_update_frequency', 'jingle_interval',
                                               'blocks', 'created_at', 'updated_at', 'analytics', 'owner', 'events',
                                      'tts_voice', 'tts_samplerate','tts_audioformat',
                                      'whitelist_number', 'outgoing_gateways', 'incoming_gateways',
                                      'primary_transmitter_phone_id', 'primary_transmitter_phone',
                                      'secondary_transmitter_phone_id', 'secondary_transmitter_phone', 'community_menu',
                                      'community_content', 'music', 'albums', 'playlists', 'artists', 'broadcast_ip',
                                               'broadcast_port', 'last_accessed_mobile', 'sip_username',
                                               'sip_password', 'sip_server', 'sip_port', 'sip_stun_server',
                                               'sip_reregister_period', 'sip_protocol', 'is_high_bandwidth',
                                               'call_volume', 'audio_volume', 'media_amplification_factor'])


class StationSynchronizationForm(StationSynchronizationFormBase):
    client_update_frequency = SelectField(_('Frequency of Synchronization (Transmission site to cloud server)'),
                                           choices=[
                                               (10, 10), (20, 20), (30, 30), (60, 60),
                                               (120, 120), (300, 300), (600, 600)
                                           ], coerce=int, default=(30, 30))
    analytic_update_frequency = DecimalField(_('Frequency of transmission site probing'),
                                             places=0,
                                             validators=[NumberRange(min=1, max=60)],
                                             default=60)
    submit = SubmitField(_('Save'))

def all_ttsvoices():
    return TtsVoice.query.all()


def all_ttssamplerates():
    return TtsSampleRate.query.all()


def all_ttsaudioformats():
    return TtsAudioFormat.query.all()

StationTtsFormBase = model_form(Station, db_session=db.session, base_class=Form,
                                      field_args={
                                          'primary_transmitter_phone': {'validators': [HasInlineForm, ]},
                                          'secondary_transmitter_phone': {'validators': [HasInlineForm, ]}},
                                      exclude=['scheduled_programs', 'blocks', 'created_at', 'updated_at', 'analytics', 'jingle_interval',
                                               'name', 'about', 'frequency', 'api_key', 'timezone', 'owner_id',
                                               'location_id', 'owner', 'location', 'languages',
                                               'client_update_frequency', 'analytic_update_frequency', 'broadcast_ip',
                                               'broadcast_port', 'community_content', 'community_menu', 'music',
                                               'playlists', 'artists', 'albums', 'network', 'last_accessed_mobile',
                                               'scheduled_programs',
                                               'blocks', 'created_at', 'updated_at', 'analytics', 'owner', 'events',
                                      'whitelist_number', 'outgoing_gateways', 'incoming_gateways',
                                      'primary_transmitter_phone_id', 'primary_transmitter_phone',
                                      'secondary_transmitter_phone_id', 'secondary_transmitter_phone', 'community_menu',
                                      'community_content', 'music', 'albums', 'playlists', 'artists', 'broadcast_ip',
                                               'broadcast_port', 'last_accessed_mobile', 'tts_language', 'sip_username',
                                               'sip_password', 'sip_server', 'sip_port', 'sip_stun_server',
                                               'sip_reregister_period', 'sip_protocol', 'is_high_bandwidth',
                                               'call_volume', 'audio_volume', 'media_amplification_factor'])


class StationTtsForm(StationSynchronizationFormBase):
    tts_voice = QuerySelectField(_('TTS Voice'), get_pk=lambda item: item.id, get_label=lambda item: "{0} ({1}-{2})".format(item.name, item.language.name, item.language.locale_code), query_factory=all_ttsvoices, allow_blank=True, blank_text=_('-select-'))
    tts_samplerate = QuerySelectField(_('Audio Quality'), get_pk=lambda item: item.id, get_label=lambda item: str(item.value) + " KHz",query_factory=all_ttssamplerates, allow_blank=True, blank_text=_('-select-'))
    tts_audioformat = QuerySelectField(_('Audio Format'), get_pk=lambda item: item.id, get_label=lambda item: item.name,query_factory=all_ttsaudioformats, allow_blank=True, blank_text=_('-select-'))
    submit = SubmitField(_('Save'))

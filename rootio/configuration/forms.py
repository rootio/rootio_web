# -*- coding: utf-8 -*-
import pytz
from flask.ext.babel import gettext as _
from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, \
    TextField, TextAreaField, HiddenField, RadioField, \
    IntegerField, FloatField, DecimalField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField, HiddenField, TextField, BooleanField, FileField
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


def stations():
    return Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()

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


class VoicePromptForm(Form):
    multipart = True
    use_tts = BooleanField(_('Use Text-to-Speech'))
    station = QuerySelectField(_('Station'), [Required()], query_factory=stations, allow_blank=False)

    on_air = FileField(_('You are now on air'))
    call_end = FileField(_('Your call will end in { seconds } seconds'))
    incoming_call = FileField(_('You have a caller on the line. To connect to the station, press one, to cancel, press two'))
    host_welcome = FileField(_('You are scheduled to host a talk show at this time. If you are ready, press one, if not ready, press two'))
    host_wait = FileField(_('Please wait while we connect you to the radio station'))
    wake_mode_activation = FileField(_('Your call will be terminated and you will be called when someone calls into the station'))
    incoming_reject_activation = FileField(_('All incoming calls will be rejected'))
    incoming_answer_activation = FileField(_('All incoming calls will be automatically answered'))
    incoming_queue_activation = FileField(_('All incoming calls will be queued for call back'))
    take_break = FileField(_('You will be called back in 5 minutes'))
    input_number = FileField(_('Please enter the number to call and press the # key to dial'))
    calling_number = FileField(_('You are calling { number }'))
    call_queued = FileField(_('Call from community caller { caller number } was queued'))
    call_failed = FileField(_('The call to { number } failed. Please pres the hash key to try again'))
    call_back_hangup = FileField(_('Thank you for wanting to take part in this program. We will call you back shortly'))
    call_back_wait = FileField(_('Please wait while we connect you to the host of this program'))

    prefetch_tts = BooleanField(_('Pre-fetch TTS'))

    on_air_txt = TextField(_('You are now on air (text)'))
    call_end_txt = TextField(_('Your call will end in { seconds } seconds (text)'))
    incoming_call_txt = TextField(_('You have a caller on the line. To connect to the station, press one, to cancel, press two (text)'))
    host_welcome_txt = TextField(_('You are scheduled to host a talk show at this time. If you are ready, press one, if not ready, press two (text)'))
    host_wait_txt = TextField(_('Please wait while we connect you to the radio station (text)'))
    wake_mode_activation_txt = TextField(_('Your call will be terminated and you will be called when someone calls into the station (text)'))
    incoming_reject_activation_txt = TextField(_('All incoming calls will be rejected (text)'))
    incoming_answer_activation_txt = TextField(_('All incoming calls will be automatically answered (text)'))
    incoming_queue_activation_txt = TextField(_('All incoming calls will be queued for call back (text)'))
    take_break_txt = TextField(_('You will be called back in 5 minutes (text)'))
    input_number_txt = TextField(_('Please enter the number to call and press the # key to dial (text)'))
    calling_number_txt = TextField(_('You are calling { number } (text)'))
    call_queued_txt = TextField(_('Call from community caller { caller number } was queued (text)'))
    call_failed_txt = TextField(_('The call to { number } failed. Please pres the hash key to try again (text)'))
    call_back_hangup_txt = TextField(_('Thank you for wanting to take part in this program. We will call you back shortly (text)'))
    call_back_wait_txt = TextField(_('Please wait while we connect you to the host of this program (text)'))

    submit = SubmitField(_('Save'))

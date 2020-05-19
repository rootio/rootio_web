# -*- coding: utf-8 -*-

import pytz
import arrow
import sqlalchemy as sa
from datetime import datetime, timedelta
from coaster.sqlalchemy import BaseMixin
from sqlalchemy_utils import JSONType
from sqlalchemy.sql import func

from .fields import FileField
from .constants import PRIVACY_TYPE

from ..utils import STRING_LEN, GENDER_TYPE, id_generator, object_list_to_named_dict
from ..extensions import db

from ..telephony.models import PhoneNumber
from sqlalchemy import or_


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


class Location(BaseMixin, db.Model):
    "A geographic location"
    __tablename__ = u'radio_location'

    name = db.Column(db.String(STRING_LEN))
    municipality = db.Column(db.String(STRING_LEN))
    district = db.Column(db.String(STRING_LEN))

    country = db.Column(db.String(STRING_LEN))
    addressline1 = db.Column(db.String(STRING_LEN))
    addressline2 = db.Column(db.String(STRING_LEN))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __unicode__(self):
        return self.name


class Language(BaseMixin, db.Model):
    __tablename__ = u'radio_language'

    name = db.Column(db.String(STRING_LEN))  # human readable language name
    iso639_1 = db.Column(db.String(2))  # 2 digit code (eg, 'en')
    iso639_2 = db.Column(db.String(3))  # 3 digit code (eg, 'eng')
    locale_code = db.Column(db.String(10))  # IETF locale (eg, 'en-US')

    # relationships
    programs = db.relationship(u'Program', backref=db.backref('language'))

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Network(BaseMixin, db.Model):
    "A network of radio stations"
    __tablename__ = "radio_network"

    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())

    stations = db.relationship(u'Station', backref=db.backref('network'))
    #programs = db.relationship(u'Program', backref=db.backref('networks'))

    # networks can have multiple admins

    def __unicode__(self):
        return self.name


t_networkusers = db.Table(
    u'radio_networkusers',
    db.Column(u'user_id', db.ForeignKey('user_user.id')),
    db.Column(u'network_id', db.ForeignKey('radio_network.id'))
)


class Station(BaseMixin, db.Model):
    "A single radio station"
    __tablename__ = 'radio_station'

    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())
    frequency = db.Column(db.Float)
    api_key = db.Column(db.String(STRING_LEN), nullable=False, default=id_generator(), unique=True)
    # todo, make sure this default function fires each time a new object is created
    timezone = db.Column(db.String(32), default="UTC")
    is_high_bandwidth = db.Column(db.Boolean, default=False)
    last_accessed_mobile = db.Column(db.DateTime(timezone=True))
    audio_volume = db.Column(db.Integer, default=8)
    call_volume = db.Column(db.Integer, default=6)
    media_amplification_factor = db.Column(db.Integer, default=0)
    jingle_interval = db.Column(db.Integer, default=10)

    # TTS settings
    tts_voice_id = db.Column(db.ForeignKey('radio_ttsvoice.id'))
    tts_samplerate_id = db.Column(db.ForeignKey('radio_ttssamplerate.id'))
    tts_audioformat_id = db.Column(db.ForeignKey('radio_ttsaudioformat.id'))
    tts_voice = db.relationship('TtsVoice', backref=db.backref('stations'))
    tts_samplerate = db.relationship('TtsSampleRate', backref=db.backref('stations'))
    tts_audioformat = db.relationship('TtsAudioFormat', backref=db.backref('stations'))

    #SIP settings
    sip_username = db.Column(db.String(STRING_LEN))
    sip_password = db.Column(db.String(STRING_LEN))
    sip_server = db.Column(db.String(STRING_LEN))
    sip_stun_server = db.Column(db.String(STRING_LEN))
    sip_port = db.Column(db.Integer, default=5060)
    sip_reregister_period = db.Column(db.Integer, default=30)
    sip_protocol = db.Column(db.String(STRING_LEN), default="udp")

    # Looping settings
    loop_ads = db.Column(db.Integer, default=3)
    loop_greetings = db.Column(db.Integer, default=3)
    loop_announcements = db.Column(db.Integer, default=3)

    # foreign keys
    #tts_language_id = db.Column(db.ForeignKey('radio_language.id'))
    owner_id = db.Column(db.ForeignKey('user_user.id'))
    network_id = db.Column(db.ForeignKey('radio_network.id'), nullable=False)
    location_id = db.Column(db.ForeignKey('radio_location.id'))
    # gateway_id = db.Column(db.ForeignKey('telephony_gateway.id'))
    primary_transmitter_phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))
    secondary_transmitter_phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    # from ..telephony.models import PhoneNumber
    # circular imports

    # relationships
    owner = db.relationship(u'User')
    location = db.relationship(u'Location')
    primary_transmitter_phone = db.relationship(u'PhoneNumber',
                                                backref=db.backref('station_primary_transmitter_phone', uselist=False),
                                                foreign_keys=[primary_transmitter_phone_id])
    secondary_transmitter_phone = db.relationship(u'PhoneNumber',
                                                  backref=db.backref('station_secondary_transmitter_phone',
                                                                     uselist=False),
                                                  foreign_keys=[secondary_transmitter_phone_id])
    # TODO, create m2m here for all whitelisted phone numbers?

    events = db.relationship(u'StationEvent', backref=db.backref('station'), lazy='dynamic')
    blocks = db.relationship(u'ScheduledBlock', backref=db.backref('station'))
    scheduled_programs = db.relationship(u'ScheduledProgram', backref=db.backref('station', uselist=False),
                                         lazy='dynamic')
    languages = db.relationship(u'Language', secondary=u'radio_stationlanguage', backref=db.backref('stations'))
    analytics = db.relationship(u'StationAnalytic', backref=db.backref('station', uselist=False), lazy='dynamic')
    outgoing_gateways = db.relationship(u'Gateway', secondary=u'radio_outgoinggateway',
                                        backref=db.backref('stations_using_for_outgoing'))
    incoming_gateways = db.relationship(u'Gateway', secondary=u'radio_incominggateway',
                                        backref=db.backref('stations_using_for_incoming'))

    whitelist_number = db.relationship(u'PhoneNumber', secondary=u'radio_whitelist', backref=db.backref('stations'))

    client_update_frequency = db.Column(db.Integer, default=60)  # in seconds
    analytic_update_frequency = db.Column(db.Integer, default=30)  # in seconds
    broadcast_ip = db.Column(db.String(16))
    broadcast_port = db.Column(db.String(16))

    @classmethod
    def get_stations(cls, current_user):
        from rootio.user import ADMIN
        from ..user.models import User
        
        if current_user.role_code == ADMIN:
            return Station.query.join(Network).join(User, Network.networkusers).all()
        else:
            return Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    def init(self):
        # load dummy program
        # init state machine
        return "init() stub"

    def successful_scheduled_programs(self):
        now = datetime.utcnow()
        return get_count(ScheduledProgram.before(now).filter(ScheduledProgram.station_id == self.id).filter(
            ScheduledProgram.status == 1).filter(ScheduledProgram.deleted == False))

    def unsuccessful_scheduled_programs(self):
        now = datetime.utcnow()
        return get_count(ScheduledProgram.before(now).filter(ScheduledProgram.station_id == self.id).filter(
            or_(ScheduledProgram.status == 0, ScheduledProgram.status == 2)).filter(ScheduledProgram.deleted == False))

    def scheduled_programs(self):
        now = datetime.utcnow()
        return get_count(ScheduledProgram.after(now).filter(ScheduledProgram.station_id == self.id).filter(ScheduledProgram.deleted == False))

    def current_program(self):
        now = datetime.now(pytz.timezone(self.timezone)).strftime('%Y-%m-%d %H:%M:%S')
        programs = ScheduledProgram.contains(now).filter_by(station_id=self.id).order_by(
            ScheduledProgram.start.desc())
        # TODO, how to resolve overlaps?
        return programs.first()

    def next_program(self):
        now = datetime.now(pytz.timezone(self.timezone)).strftime('%Y-%m-%d %H:%M:%S')
        upcoming_programs = ScheduledProgram.after(now).filter_by(station_id=self.id).order_by(
            ScheduledProgram.start.asc())
        # TODO, how to resolve overlaps?
        return upcoming_programs.first()

    def previous_program(self):
        now = datetime.now(pytz.timezone(self.timezone)).strftime('%Y-%m-%d %H:%M:%S')
        upcoming_programs = ScheduledProgram.before(now).filter_by(station_id=self.id).order_by(
            ScheduledProgram.start.desc())
        # TODO, how to resolve overlaps?
        return upcoming_programs.first()

    def current_block(self):
        now = datetime.utcnow().time()  # blocks not date specific, time only
        blocks = ScheduledBlock.contains(now).filter_by(station_id=self.id)
        # TODO, how to resolve overlaps?
        return blocks.first()

    def status(self):
        # TODO

        # random appearance for demo
        from random import random
        r = random()
        if r > 0.8:
            return "unknown"
        elif r > 0.6:
            return "off"
        else:
            return "on"

    def recent_analytics(self, days_ago=7):
        since_date = datetime.utcnow() - timedelta(days=days_ago)

        analytics_list = StationAnalytic.query \
            .filter_by(station_id=self.id) \
            .order_by(StationAnalytic.id.desc()).limit(10)
        # convert to named dict for sparkline display
        analytics_dict = object_list_to_named_dict(analytics_list)
        return analytics_dict

    def __unicode__(self):
        return self.name


t_stationlanguage = db.Table(
    u'radio_stationlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)

t_station_outgoinggateway = db.Table(
    u'radio_outgoinggateway',
    db.Column(u'outgoinggateway_id', db.ForeignKey('telephony_gateway.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)

t_station_incominggateway = db.Table(
    u'radio_incominggateway',
    db.Column(u'incominggateway_id', db.ForeignKey('telephony_gateway.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)

t_station_whitelist = db.Table(
    u'radio_whitelist',
    db.Column(u'phone_id', db.ForeignKey('telephony_phonenumber.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)


class ProgramType(BaseMixin, db.Model):
    """A flexible definition of program dynamics, with python script (definition) for the definition
       and json description (phone_functions) of necessary functions, media, &etc the phone will have to run."""
    __tablename__ = u'radio_programtype'

    name = db.Column(db.String(STRING_LEN), nullable=False)
    description = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    phone_functions = db.Column(db.Text, nullable=False)

    def __unicode__(self):
        return self.name


class Program(BaseMixin, db.Model):
    "A single or recurring radio program"
    __tablename__ = 'radio_program'

    name = db.Column(db.String(STRING_LEN),
                     nullable=False)
    description = db.Column(db.Text, nullable=True)
    structure = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Interval)
    deleted = db.Column(db.Boolean)
    update_recurrence = db.Column(db.Text())  # when new content updates are available

    language_id = db.Column(db.ForeignKey('radio_language.id'))
    program_type_id = db.Column(db.ForeignKey('radio_programtype.id'))

    program_type = db.relationship(u'ProgramType')
    episodes = db.relationship('Episode', backref=db.backref('program'), lazy='dynamic')
    scheduled_programs = db.relationship(u'ScheduledProgram', backref=db.backref('program', uselist=False))
    networks = db.relationship(u'Network', secondary=u'radio_programnetwork', backref=db.backref('programs'))

    def __unicode__(self):
        return self.name

    def episodes_aired(self):
        now = datetime.utcnow()
        return ScheduledProgram.before(now).filter(ScheduledProgram.program_id == self.id).filter(
            ScheduledProgram.status == 1).filter(ScheduledProgram.deleted == False).all()

t_programnetwork = db.Table(
    u'radio_programnetwork',
    db.Column(u'network_id', db.ForeignKey('radio_network.id')),
    db.Column(u'program_id', db.ForeignKey('radio_program.id'))
)

class Episode(BaseMixin, db.Model):
    "A particular episode of a program, or other broadcast audio"
    __tablename__ = 'radio_episode'

    program_id = db.Column(db.ForeignKey('radio_program.id'), nullable=False)
    recording_id = db.Column(db.ForeignKey('radio_recording.id'))

    recording = db.relationship(u'Recording')


class ScheduledBlock(BaseMixin, db.Model):
    """A block of similar programs, with a recurrence rule, start_time, and end_time.
    Similar to advertising 'dayparts'
    """
    __tablename__ = "radio_scheduledblock"

    name = db.Column(db.String(STRING_LEN), nullable=False)
    recurrence = db.Column(db.Text())  # iCal rrule format, RFC2445 4.8.5.4
    start_time = db.Column(db.Time(timezone=False), nullable=False)
    end_time = db.Column(db.Time(timezone=False), nullable=False)
    station_id = db.Column(db.ForeignKey('radio_station.id'))

    @classmethod
    def after(cls, time):
        return cls.query.filter(ScheduledBlock.start_time >= time)

    @classmethod
    def before(cls, time):
        return cls.query.filter(ScheduledBlock.end_time <= time)

    @classmethod
    def between(cls, start, end):
        return cls.query.filter(ScheduledBlock.start_time > start) \
            .filter(ScheduledBlock.end_time < end)

    @classmethod
    def contains(cls, time):
        return cls.query.filter(ScheduledBlock.start_time <= time) \
            .filter(ScheduledBlock.end_time >= time)

    def __unicode__(self):
        return self.name


class ScheduledProgram(BaseMixin, db.Model):
    """Content scheduled to air on a station at a time.
    Read these in order to determine a station's next to air."""
    __tablename__ = "radio_scheduledprogram" 

    station_id = db.Column(db.ForeignKey('radio_station.id'))
    program_id = db.Column(db.ForeignKey('radio_program.id'))
    status = db.Column(db.Integer)
    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted = db.Column(db.Boolean)
    station = db.relationship(u'Station')

    # For recurring events - add a unique string to identify all items in the series
    series_id = db.Column(db.String(STRING_LEN), nullable=True)

    '''
    @property
    def station(self):
        return Station.query.filter(Station.id == self.station_id).first()
    '''
    
    @property
    def start_local(self):
        timezone = pytz.timezone(self.station.timezone)
        offset = int(timezone.localize(datetime.now()).strftime('%z')[:3])
        result = self.start.replace(tzinfo=None) - timedelta(hours=offset)
        return result.replace(tzinfo=pytz.utc).astimezone(timezone)

    @property
    def start_utc(self):
        timezone = pytz.timezone(self.station.timezone)
        offset = int(timezone.localize(datetime.now()).strftime('%z')[:3])
        result = self.start.replace(tzinfo=None) - timedelta(hours=offset)
        return result.replace(tzinfo=pytz.utc)

    @classmethod
    def after(cls, date):
        return cls.query.filter(ScheduledProgram.start >= date)

    @classmethod
    def before(cls, date):
        return cls.query.filter(ScheduledProgram.end <= date)

    @classmethod
    def between(cls, start, end):
        return cls.query.filter(ScheduledProgram.start >= start) \
            .filter(ScheduledProgram.end <= end)

    @classmethod
    def contains(cls, date):
        return cls.query.filter(ScheduledProgram.start <= date) \
            .filter(ScheduledProgram.end >= date)

    def __unicode__(self):
        return "%s at %s" % (self.program.name, self.start)


class PaddingContent(BaseMixin, db.Model):
    """An advertisement or PSA to run on a network in a block.
    Actual air schedule to be determined by the scheduler."""
    __tablename__ = "radio_paddingcontent"

    recording_id = db.Column(db.ForeignKey('radio_recording.id'))
    block_id = db.Column(db.ForeignKey('radio_scheduledblock.id'))
    # sponsoring org?

    block = db.relationship(u'ScheduledBlock')
    networks = db.relationship(u'Network', secondary=u'radio_networkpadding', backref=db.backref('paddingcontents'))


t_networkpadding = db.Table(
    u'radio_networkpadding',
    db.Column(u'network_id', db.ForeignKey('radio_network.id')),
    db.Column(u'paddingcontent_id', db.ForeignKey('radio_paddingcontent.id'))
)


class Recording(BaseMixin, db.Model):
    "A recorded sound file"
    __tablename__ = 'radio_recording'

    url = db.Column(db.String(160))
    local_file = db.Column(FileField([]))


class Person(BaseMixin, db.Model):
    "A person associated with a station or program, but not necessarily a user of Rootio system"
    __tablename__ = 'radio_person'
    # from ..telephony.models import PhoneNumber
    # circular imports

    title = db.Column(db.String(8))
    firstname = db.Column(db.String(STRING_LEN))
    middlename = db.Column(db.String(STRING_LEN))
    lastname = db.Column(db.String(STRING_LEN))
    email = db.Column(db.String(STRING_LEN))
    additionalcontact = db.Column(db.String(STRING_LEN))

    phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    phone = db.relationship(u'PhoneNumber', backref=db.backref('person', uselist=False))
    role = db.relationship(u'Role', backref=db.backref('person'))
    languages = db.relationship(u'Language', secondary=u'radio_personlanguage', backref=db.backref('person'))
    network_id = db.Column(db.ForeignKey('radio_network.id'))
    networks = db.relationship(u'Network', secondary=u'radio_personnetwork', backref=db.backref('people'))
    gender_code = db.Column(db.Integer)

    deleted = db.Column(db.Boolean, default=False)

    @property
    def gender(self):
        return GENDER_TYPE.get(self.gender_code)

    privacy_code = db.Column(db.Integer)

    @property
    def privacy(self):
        return PRIVACY_TYPE.get(self.privacy_code)

    def __unicode__(self):
        return " ".join(filter(None, (self.title, self.firstname, self.middlename, self.lastname)))

    # TODO: fk to user_id?


t_personnetwork = db.Table(
    u'radio_personnetwork',
    db.Column(u'network_id', db.ForeignKey('radio_network.id')),
    db.Column(u'person_id', db.ForeignKey('radio_person.id'))
)

t_personlanguage = db.Table(
    u'radio_personlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id')),
    db.Column(u'person_id', db.ForeignKey('radio_person.id'))
)


class Role(BaseMixin, db.Model):
    "A role for a person at a particular station"
    __tablename__ = u'radio_role'

    name = db.Column(db.String)
    person_id = db.Column(db.ForeignKey('radio_person.id'))
    # TODO: add program_id
    station_id = db.Column(db.ForeignKey('radio_station.id'))


class StationAnalytic(BaseMixin, db.Model):
    "A store for analytics from the client"
    __tablename__ = 'radio_stationanalytic'

    station_id = db.Column(db.ForeignKey('radio_station.id'))

    battery_level = db.Column(db.Integer) # percentage 0,100

    gsm_signal_1 = db.Column(db.Integer)  # signal strength in db (sim 1)
    gsm_network_type_1 = db.Column(db.String(30)) # gsm network type (edge / lte / hspa etc) (sim 1)
    gsm_network_name_1 = db.Column(db.String(30)) # gsm network name for sim 1
    gsm_network_connected_1 = db.Column(db.Boolean, default=False)

    gsm_signal_2 = db.Column(db.Integer)  # signal strength in db (sim 2)
    gsm_network_type_2 = db.Column(db.String(30)) # gsm network type (edge / lte / hspa etc) (sim 2)
    gsm_network_name_2 = db.Column(db.String(30)) # gsm network name for sim 2
    gsm_network_connected_2 = db.Column(db.Boolean, default=False)

    wifi_connectivity = db.Column(db.Float)  # boolean 0/1
    memory_utilization = db.Column(db.Float)  # percentage 0,100
    storage_usage = db.Column(db.Float)  # percentage 0,100
    cpu_load = db.Column(db.Float)  # percentage 0,100
    gps_lat = db.Column(db.Float)  # location of the handset
    gps_lon = db.Column(db.Float)  #
    record_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __unicode__(self):
        return "%s @ %s" % (self.station.name, self.created_at.strftime("%Y-%m-%d %H:%M:%S"))


class ContentType(BaseMixin, db.Model):
    __tablename__ = u'content_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __unicode__(self):
        return self.name


class TtsAudioFormat(BaseMixin, db.Model):
    __tablename__ = 'radio_ttsaudioformat'

    name = db.Column(db.String(30), nullable=False)


class TtsSampleRate(BaseMixin, db.Model):
    __tablename__ = 'radio_ttssamplerate'

    value = db.Column(db.Integer(), nullable=False)


class TtsVoice(BaseMixin, db.Model):
    __tablename__ = 'radio_ttsvoice'

    name = db.Column(db.String(30), nullable=False)
    language_id = db.Column(db.ForeignKey('radio_language.id'))
    gender_code = db.Column(db.Integer())
    language = db.relationship('Language', backref=db.backref('tts_voices'))


class StationEvent(BaseMixin, db.Model):
    __tablename__ = 'radio_stationevent'

    id = db.Column(db.BigInteger, primary_key=True)
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    date = db.Column(db.DateTime(timezone=True))
    category = db.Column(db.String(STRING_LEN), nullable=False)
    action = db.Column(db.String(STRING_LEN), nullable=False)
    content = db.Column(db.Text, nullable=False)

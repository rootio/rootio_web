# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from coaster.sqlalchemy import BaseMixin
from sqlalchemy_utils import JSONType
from sqlalchemy.sql import func

from .fields import FileField
from .constants import PRIVACY_TYPE

from ..utils import STRING_LEN, GENDER_TYPE, id_generator, object_list_to_named_dict
from ..extensions import db

from ..telephony.models import PhoneNumber


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

    # TTS settings
    # TODO: make these fields foreign keys once we figure out how the values would look like
    tts_accent = db.Column(db.String(STRING_LEN))
    tts_gender = db.Column(db.String(STRING_LEN))
    tts_audio_format = db.Column(db.String(STRING_LEN))
    tts_sample_rate = db.Column(db.String(STRING_LEN))

    #SIP settings
    sip_username = db.Column(db.String(STRING_LEN))
    sip_password = db.Column(db.String(STRING_LEN))
    sip_server = db.Column(db.String(STRING_LEN))
    sip_stun_server = db.Column(db.String(STRING_LEN))
    sip_port = db.Column(db.Integer, default=5060)
    sip_reregister_period = db.Column(db.Integer, default=30)
    sip_protocol = db.Column(db.String(STRING_LEN), default="udp")

    # foreign keys
    tts_language_id = db.Column(db.ForeignKey('radio_language.id'))
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
    tts_language = db.relationship(u'Language')
    location = db.relationship(u'Location')
    primary_transmitter_phone = db.relationship(u'PhoneNumber',
                                                backref=db.backref('station_primary_transmitter_phone', uselist=False),
                                                foreign_keys=[primary_transmitter_phone_id])
    secondary_transmitter_phone = db.relationship(u'PhoneNumber',
                                                  backref=db.backref('station_secondary_transmitter_phone',
                                                                     uselist=False),
                                                  foreign_keys=[secondary_transmitter_phone_id])
    # TODO, create m2m here for all whitelisted phone numbers?

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

    client_update_frequency = db.Column(db.Float)  # in seconds
    analytic_update_frequency = db.Column(db.Float)  # in seconds
    broadcast_ip = db.Column(db.String(16))
    broadcast_port = db.Column(db.String(16))

    def init(self):
        # load dummy program
        # init state machine
        return "init() stub"

    def successful_scheduled_programs(self):
        now = datetime.utcnow()
        return ScheduledProgram.before(now).filter(ScheduledProgram.station_id == self.id).filter(
            ScheduledProgram.status == True).filter(ScheduledProgram.deleted == False).all()

    def unsuccessful_scheduled_programs(self):
        now = datetime.utcnow()
        return ScheduledProgram.before(now).filter(ScheduledProgram.station_id == self.id).filter(
            ScheduledProgram.status == False).filter(ScheduledProgram.deleted == False).all()

    def scheduled_programs(self):
        now = datetime.utcnow()
        return ScheduledProgram.after(now).filter(ScheduledProgram.deleted == False).all()

    def current_program(self):
        now = datetime.utcnow()
        programs = ScheduledProgram.contains(now).filter_by(station_id=self.id)
        # TODO, how to resolve overlaps?
        return programs.first()

    def next_program(self):
        now = datetime.utcnow()
        upcoming_programs = ScheduledProgram.after(now).filter_by(station_id=self.id).order_by(
            ScheduledProgram.start.asc())
        # TODO, how to resolve overlaps?
        return upcoming_programs.first()

    def previous_program(self):
        now = datetime.utcnow()
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
            ScheduledProgram.status == True).filter(ScheduledProgram.deleted == False).all()

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
    status = db.Column(db.Boolean)
    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted = db.Column(db.Boolean)

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

    battery_level = db.Column(db.Integer)  # percentage 0,100
    gsm_signal = db.Column(db.Integer)  # signal strength in db
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

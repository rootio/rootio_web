# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, types
from .fields import FileField
from .constants import PROGRAM_TYPES, PRIVACY_TYPE

from ..utils import STRING_LEN, GENDER_TYPE, get_current_time
from ..extensions import db

from ..telephony import PhoneNumber

class Location(db.Model):
    "A geographic location"
    __tablename__ = u'radio_location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN))
    municipality = db.Column(db.String(STRING_LEN))
    district = db.Column(db.String(STRING_LEN))
    modifieddate = db.Column(db.Date)
    country = db.Column(db.String(STRING_LEN))
    addressline1 = db.Column(db.String(STRING_LEN))
    addressline2 = db.Column(db.String(STRING_LEN))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class Language(db.Model):
    __tablename__ = u'radio_language'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN)) # human readable language name
    iso639_1 = db.Column(db.String(2)) # 2 digit code (eg, 'en')
    iso639_2 = db.Column(db.String(3))# 3 digit code (eg, 'eng')
    locale_code = db.Column(db.String(10)) # IETF locale (eg, 'en-US')

    #relationships
    programs = db.relationship(u'Program', backref=db.backref('language'))

    def __unicode__(self):
        return self.name

class Network(db.Model):
    "A network of radio stations"
    __tablename__ = "radio_network"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())

    admins = db.relationship(u'User', secondary=u'radio_networkadmins', backref=db.backref('networks'))
    stations = db.relationship(u'Station', backref=db.backref('network'))
    #networks can have multiple admins


t_networkadmins = db.Table(
    u'radio_networkadmins',
    db.Column(u'user_id', db.ForeignKey('user_user.id')),
    db.Column(u'network_id', db.ForeignKey('radio_network.id'))
)


class Station(db.Model):
    "A single radio station"
    __tablename__ = 'radio_station'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())
    frequency = db.Column(db.Float)

    #foreign keys
    owner_id = db.Column(db.ForeignKey('user_user.id'))
    network_id = db.Column(db.ForeignKey('radio_network.id'))
    location_id = db.Column(db.ForeignKey('radio_location.id'))
    phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    #relationships
    owner = db.relationship(u'User')
    location = db.relationship(u'Location')
    phone = db.relationship(u'PhoneNumber')
    schedules = db.relationship(u'ProgramSchedule', backref=db.backref('station'))
    scheduled_episodes = db.relationship(u'ScheduledEpisode', backref=db.backref('station'))
    languages = db.relationship(u'Language', secondary=u'radio_stationlanguage', backref=db.backref('stations'))

    @property
    def current_program(self):
        #TODO
        return "current_program() stub"

    @property
    def status(self):
        #TODO
        return "status() stub"


t_stationlanguage = db.Table(
    u'radio_stationlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)


class ProgramType(db.Model):
    "A flexible definition of program dynamics"
    __tablename__ = u'radio_programtype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN),nullable=False)
    definition = db.Column(db.PickleType)
    #todo program definition


class Program(db.Model):
    "A single or recurring radio program"
    __tablename__ = 'radio_program'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN),
        nullable=False)
    length = db.Column(db.Time)
    update_recurrence = db.Column(db.Text()) #when new episodes are available

    language_id = db.Column(db.ForeignKey('radio_language.id'))
    program_type_id = db.Column(db.ForeignKey('radio_programtype.id'))

    episodes = db.relationship('Episode', backref=db.backref('program'), lazy='dynamic')


class Episode(db.Model):
    "A particular instance of a program"
    __tablename__ = 'radio_episode'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.ForeignKey('radio_program.id'))
    recording_id = db.Column(db.ForeignKey('radio_recording.id'))
    created_time = db.Column(db.DateTime, default=get_current_time)

    recording = db.relationship(u'Recording')


class ProgramSchedule(db.Model):
    "A commitment by a station to air a program on a recurring schedule"
    __tablename__ = "radio_programschedule"
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    program_id = db.Column(db.ForeignKey('radio_program.id'))
    recurrence = db.Column(db.Text()) #iCal rrule format, RFC2445 4.8.5.4

    program = db.relationship(u'Program')


class ScheduledEpisode(db.Model):
    "An episode scheduled to air on a station at a time"
    __tablename__ = "radio_scheduledepisode"
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    program_id = db.Column(db.ForeignKey('radio_episode.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)


class Recording(db.Model):
    "A recorded sound file"
    __tablename__ = 'radio_recording'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(160))
    local_file = db.Column(FileField([]))
    created_time = db.Column(db.DateTime, default=get_current_time)


class Person(db.Model):
    "A person associated with a station or program, but not necessarily a user of Rootio system"
    __tablename__ = 'radio_person'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(8))
    firstname = db.Column(db.String(STRING_LEN))
    middlename = db.Column(db.String(STRING_LEN))
    lastname = db.Column(db.String(STRING_LEN))
    email = db.Column(db.String(STRING_LEN))
    additionalcontact = db.Column(db.String(STRING_LEN))

    phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    phone = db.relationship(u'PhoneNumber', backref=db.backref('person'))
    role = db.relationship(u'Role', backref=db.backref('person'))
    languages = db.relationship(u'Language', secondary=u'radio_personlanguage', backref=db.backref('person'))

    gender_code = db.Column(db.Integer)
    @property
    def gender(self):
        return GENDER_TYPE.get(self.gender_code)

    privacy_code = db.Column(db.Integer)
    @property
    def privacy(self):
        return PRIVACY_TYPE.get(self.privacy_code)


t_personlanguage = db.Table(
    u'radio_personlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id'), primary_key=True),
    db.Column(u'person_id', db.ForeignKey('radio_person.id'), primary_key=True)
)

class Role(db.Model):
    "A role for a person at a particular station"
    __tablename__ = u'radio_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    person_id = db.Column(db.ForeignKey('radio_person.id'))
    station_id = db.Column(db.ForeignKey('radio_station.id'))

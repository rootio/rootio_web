# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, types
from .fields import FileField
from .constants import PROGRAM_TYPES, PRIVACY_TYPE

from ..utils import STRING_LEN, SEX_TYPE, get_current_time
from ..extensions import db


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


class Station(db.Model):
    "A single radio station"
    __tablename__ = 'radio_station'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())
    frequency = db.Column(db.Float)

    #foreign keys
    owner_id = db.Column(db.ForeignKey('user_users.id'))
    location_id = db.Column(db.ForeignKey('radio_location.id'))
    phone_id = db.Column(db.ForeignKey('radio_phonenumber.id'))

    #relationships
    owner = db.relationship(u'User')
    location = db.relationship(u'Location')
    phone = db.relationship(u'PhoneNumber')
    languages = db.relationship(u'Language', secondary=u'stationlanguage', backref=db.backref('stations'))

    @property
    def current_program(self):
        #TODO
        return "current_program() stub"

    @property
    def status(self):
        #TODO
        return "status() stub"


t_stationlanguage = db.Table(
    u'stationlanguage',
    db.Column(u'language_pk', db.ForeignKey('radio_language.id'), primary_key=True),
    db.Column(u'station_pk', db.ForeignKey('radio_station.id'), primary_key=True)
)


class Program(db.Model):
    "A recurring radio program"
    __tablename__ = 'radio_program'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN),
        nullable=False)
    length = db.Column(db.Time)
    language = db.Column(db.String(5))
    
    program_type = db.Column(db.SmallInteger, default=0)
    @property
    def type(self):
        return PROGRAM_TYPE[self.program_type]

    episodes = db.relationship('Episode', backref=db.backref('program'), lazy='dynamic')


class Episode(db.Model):
    "A particular instance of a program"
    __tablename__ = 'radio_episode'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('radio_program.id'))
    saved_file = db.Column(FileField([]))
    created_time = db.Column(db.DateTime, default=get_current_time)


class PhoneNumber(db.Model):
    "A phone number, associated with a station or a person"
    __tablename__ = u'radio_phonenumber'

    id = db.Column(db.Integer, primary_key=True)
    phonenumbertype = db.Column(db.String(30)) #constrain to mobile / landline?
    carrier = db.Column(db.String(STRING_LEN))
    countrycode = db.Column(db.String(3)) #does not include + symbol
    areacode = db.Column(db.String(8)) #consistent across countries?
    number = db.Column(db.String(20))


class Person(db.Model):
    "A person associated with a station or program, but not necessarily a user of Rootio system"
    __tablename__ = 'radio_person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN))
    phone_id = db.Column(db.ForeignKey('radio_phonenumber.id'))

    phone = db.relationship(u'PhoneNumber', backref=db.backref('phonenumbers'))
    
    sex_code = db.Column(db.Integer)
    @property
    def sex(self):
        return SEX_TYPE.get(self.sex_code)

    privacy_code = db.Column(db.Integer)
    @property

    def privacy(self):
        return PRIVACY_TYPE.get(self.privacy_code)


class Role(db.Model):
    "A role for a person at a particular station"
    __tablename__ = u'radio_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    person_id = db.Column(db.ForeignKey('radio_person.id'))
    station_id = db.Column(db.ForeignKey('radio_station.id'))

    person = db.relationship(u'Person')
    station = db.relationship(u'Station')

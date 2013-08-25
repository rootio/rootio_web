# -*- coding: utf-8 -*-

from sqlalchemy import Column, types
from .fields import FileField
from .constants import PROGRAM_TYPES, PRIVACY_TYPE
#hardcode initially, but should probably be tied to program dynamics

from ..utils import STRING_LEN, SEX_TYPE, get_current_time
from ..extensions import db


class Station(db.Model):
    "A single radio station"
    __tablename__ = 'radio_station'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN),
        nullable=False)
    frequency = Column(db.Float())
    phone = Column(db.String(STRING_LEN),
        nullable=False)
    contact = Column(db.String(STRING_LEN),
        nullable=False)
    owner_id = Column(db.Integer, db.ForeignKey('users.id'))
    location = Column(db.String(STRING_LEN))
    latitude = Column(db.Float())
    longitude = Column(db.Float())
    about = Column(db.Text())

    network = Column(db.String(STRING_LEN)) #constrain to set? fk?

    @property
    def current_program(self):
        #TODO
        return "temp current program"

    @property
    def status(self):
        #TODO
        return "temp status"

class Program(db.Model):
    "A recurring radio program"
    __tablename__ = 'radio_program'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN),
        nullable=False)
    length = Column(db.Time())
    language = Column(db.String(5)) #constrain to set of langs in app.config.ACCEPT_LANGUAGES ?
    
    program_type = Column(db.SmallInteger, default=0)
    @property
    def type(self):
        return PROGRAM_TYPE[self.program_type]

    episodes = db.relationship('Episode', backref='program', lazy='dynamic')

class Episode(db.Model):
    "A particular instance of a program"
    __tablename__ = 'radio_episode'

    id = Column(db.Integer, primary_key=True)
    program_id = Column(db.Integer, db.ForeignKey('radio_program.id'))
    saved_file = Column(FileField([]))
    created_time = Column(db.DateTime, default=get_current_time)

class Person(db.Model):
    __tablename__ = 'radio_person'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN))
    phone = Column(db.String(STRING_LEN))
    
    sex_code = db.Column(db.Integer)
    @property
    def sex(self):
        return SEX_TYPE.get(self.sex_code)

    privacy_code = db.Column(db.Integer)
    @property
    def privacy(self):
        return PRIVACY_TYPE.get(self.privacy_code)

    # entity_id = Column(db.Integer, db.ForeignKey('entity.id'))    

# class Entity(db.Model):
#     ""
#     __tablename__ = "radio_entity"

#     id = Column(db.Integer, primary_key=True)
#     members = db.relationship('Person', backref='entity', lazy='dynamic')
    

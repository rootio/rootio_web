# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table
from ..extensions import db

from .constants import PHONE_NUMBER_TYPE
from ..utils import STRING_LEN

class PhoneNumber(db.Model):
    """A phone number, associated with a station, person or call.
    Usually created by the telephony server, but can be edited via the web interface.
    """
    __tablename__ = u'telephony_phonenumber'

    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(STRING_LEN))
    countrycode = db.Column(db.String(3)) #does not include + symbol
    number = db.Column(db.String(20),nullable=False) #filtered data
    raw_number = db.Column(db.String(20)) #raw from telephony

    number_type = db.Column(db.Integer) #convert to enum?
    @property
    def type(self):
        return PHONE_NUMBER_TYPE.get(self.number_type)

    def __unicode__(self):
        if self.countrycode:
            return "+%s %s" % (self.countrycode, self.number)
        else:
            return self.number


class Call(db.Model):
    """An incoming or outgoing call from the telephony system.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = u'telephony_call'

    id = db.Column(db.Integer, primary_key=True)
    call_uuid = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    from_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id')) #nullable=False?
    to_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id')) #nullable=False?
    a_leg_uuid = db.Column(db.String(100)) #only for outgoing
    a_leg_request_uuid = db.Column(db.String(100)) #only for outgoing
    onairprogram_id = db.Column(db.ForeignKey('onair_program.id'))

    from_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Call.from_phonenumber_id == PhoneNumber.id')
    to_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Call.to_phonenumber_id == PhoneNumber.id')


class Message(db.Model):
    """An incoming or outgoing text message from the telephony system.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = u'telephony_message'

    id = db.Column(db.Integer, primary_key=True)
    message_uuid = db.Column(db.String(100))
    sendtime = db.Column(db.DateTime)
    text = db.Column(db.String(160))
    from_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id')) #nullable=False?
    to_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id')) #nullable=False?
    onairprogram_id = db.Column(db.ForeignKey('onair_program.id'))

    from_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Message.from_phonenumber_id == PhoneNumber.id')
    to_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Message.to_phonenumber_id == PhoneNumber.id')

class Gateway(db.Model):
    """A sip gateway specification, one (current) or more (TODO) per station"""
    __tablename__ = u'telephony_gateway'

    id = db.Column(db.Integer, primary_key=True)
    number_top = db.Column(db.Integer)
    number_bottom = db.Column(db.Integer)
    sofia_string = db.Column(db.String(160))
    extra_string = db.Column(db.String(300))



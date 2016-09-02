# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table
from ..extensions import db

from .constants import PHONE_NUMBER_TYPE
from ..utils import STRING_LEN
#from ..radio.models import Station
    

from coaster.sqlalchemy import BaseMixin

class PhoneNumber(BaseMixin, db.Model):
    """A phone number, associated with a station, person or call.
    Usually created by the telephony server, but can be edited via the web interface.
    """
    __tablename__ = u'telephony_phonenumber'

    
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


class Call(BaseMixin, db.Model):
    """An incoming or outgoing call from the telephony system.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    #from rootio.radio.models import Station
    #ugh, circular imports...
    __tablename__ = u'telephony_call'

    
    call_uuid = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    from_phonenumber = db.Column(db.String(20)) #nullable=False?
    to_phonenumber = db.Column(db.String(20)) #nullable=False?
    a_leg_uuid = db.Column(db.String(100)) #only for outgoing
    a_leg_request_uuid = db.Column(db.String(100)) #only for outgoing
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    onairprogram_id = db.Column(db.ForeignKey('onair_program.id'))
    
    #todo: add station relationship
    #station = db.relationship(u'Station')
   


class Message(BaseMixin, db.Model):
    """An incoming or outgoing text message from the telephony system.
    Defined here for easy readability by the web server, but should not be written to in this process."""
    __tablename__ = u'telephony_message'

    
    message_uuid = db.Column(db.String(100))
    sendtime = db.Column(db.DateTime)
    text = db.Column(db.Text())
    from_phonenumber = db.Column(db.String(20)) #nullable=False?
    to_phonenumber = db.Column(db.String(20)) #nullable=False?
    station_id = db.Column(db.ForeignKey('radio_station.id')) 
    onairprogram_id = db.Column(db.ForeignKey('onair_program.id'))

  
class Gateway(BaseMixin, db.Model):
    """A sip gateway specification, one (current) or more (TODO) per station"""
    __tablename__ = u'telephony_gateway'

    name = db.Column(db.String(100))
    number_top = db.Column(db.Integer)
    number_bottom = db.Column(db.Integer)
    sofia_string = db.Column(db.String(160))
    extra_string = db.Column(db.String(300))
    gateway_prefix = db.Column(db.String(20))
    is_goip = db.Column(db.Boolean)

    def __unicode__(self):
        return self.name
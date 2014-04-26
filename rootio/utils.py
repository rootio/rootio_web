# -*- coding: utf-8 -*-
"""
    Utils has nothing to do with models and views.
"""

import string
import random
import os

from datetime import datetime, time, timedelta

from flask import Flask
from flask import json
from flask.ext.wtf import Form

ALLOWED_AVATAR_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Form validation

USERNAME_LEN_MIN = 4
USERNAME_LEN_MAX = 25

REALNAME_LEN_MIN = 4
REALNAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 16

AGE_MIN = 1
AGE_MAX = 120

# Gender type.
MALE = 1
FEMALE = 2
OTHER = 9
GENDER_TYPE = {
    MALE: u'Male',
    FEMALE: u'Female',
    OTHER: u'Other',
}

# Model
STRING_LEN = 100

def get_current_time():
    return datetime.utcnow()


def pretty_date(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_AVATAR_EXTENSIONS


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    #return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception, e:
        raise e

#convert a form errors to an error dict for json display
def error_dict(form_errors):
    d = {}
    for (field,messages) in form_errors.items():
        msgs = []
        for m in messages:
            msgs.append(unicode(m))
        d[field] = ". ".join(msgs)
    return d


def object_list_to_named_dict(object_list):
    """convert from object list to dict of values
    for display as sparkline"""
    named_dict = {}
    for a in object_list:
        for (k,v) in a.__dict__.items():
            #skip privates
            if k.startswith('_'):
                continue
            if k in named_dict:
                named_dict[k].append(v)
            else:
                named_dict[k] = [v]
    return named_dict

def fk_lookup_form_data(model_dict,data):
    """Checks to ensure all named models have an object with the specified id
    Takes a dict of model names and classes
    and form dict with fields and values

    Modifies form dict, replacing id int with object reference

    Returns JSON error dict if lookup error, False otherwise """
    for (field,cls) in model_dict.items():
        try:
            data[field] = cls.query.get(int(data[field]))
        except ValueError:
            response = {'status':'error','errors':{field:_('Invalid ')+field},'status_code':400}
            return response
    return False


def simple_serialize_sqlalchemy(model):
    """really naive way of serializing a sqlalchemy model to a dictionary
    no joins, model attributes only
    ignores privates"""
    if hasattr(model, '__dict__'):
        keys = [key for key in model.__dict__.keys() if not key.startswith('_')]
        serial_dict = {attr: getattr(model, attr) for attr in keys}
        return serial_dict
    else:
        return model


class CustomJSONEncoder(json.JSONEncoder):
    """custom json encoder class that can handle python datetimes
    Drops microseconds, because Android client doesn't like it so precise"""
    def default(self, obj):
        if isinstance(obj,datetime):
            return datetime.isoformat(obj.replace(microsecond=0))
        if isinstance(obj, time):
            return time.isoformat(obj.replace(microsecond=0))
        if isinstance(obj, timedelta):
            return str(obj)
        #add support for other serialization formats here...
        return super(CustomJSONEncoder, self).default(obj)


#monkey patch wtforms to allow field_order attribute
#from http://stackoverflow.com/a/18475322
class OrderedForm(Form):
    def __iter__(self):
        field_order = getattr(self, 'field_order', None)
        if field_order:
            temp_fields = []
            for name in field_order:
                if name == '*':
                    temp_fields.extend([f for f in self._unbound_fields if f[0] not in field_order])
                else:
                    temp_fields.append([f for f in self._unbound_fields if f[0] == name][0])
            self._unbound_fields = temp_fields
        return super(OrderedForm, self).__iter__()

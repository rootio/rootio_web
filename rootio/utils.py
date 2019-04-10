# -*- coding: utf-8 -*-
"""
    Utils has nothing to do with models and views.
"""

import os
import random
import re
import string
import urllib
from datetime import datetime, time, timedelta

import yaml
import boto3
import sox
from flask import json
from flask.ext.wtf import Form
from sqlalchemy import or_, text
from werkzeug.utils import secure_filename

from .config import DefaultConfig

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


def format_log_line(line):
    parts = line.split('|')
    text = parts[1].strip().split(' ')

    action = text[1]
    details = yaml.load(
        ' '.join(text[2:]).replace(', ', '\n')
    )

    return {
        'date': parts[0],
        'type': text[0],
        'action': action,
        'details': details,
    }

def upload_to_s3(file, key,  acl="public-read"):
    bucket_name = DefaultConfig.S3_BUCKET_NAME
    s3 = boto3.client('s3',
                      DefaultConfig.S3_REGION,
                      aws_access_key_id=DefaultConfig.S3_KEY_ID,
                      aws_secret_access_key=DefaultConfig.S3_KEY
                      )
    s3.upload_fileobj(
        file,
        bucket_name,
        key,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )

    bucket_location = s3.get_bucket_location(Bucket=bucket_name)
    uri = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        bucket_name,
        urllib.quote(key)
    )

    return uri


def save_uploaded_file(uploaded_file, directory, file_name=False, process_audio=True):
    date_part = datetime.now().strftime("%y%m%d%H%M%S")
    if not file_name:
        file_name = "{0}_{1}".format(date_part, uploaded_file.filename)
        file_name = secure_filename(file_name)

    if DefaultConfig.S3_UPLOADS:
        try:
            location = upload_to_s3(uploaded_file, file_name)
        except:
            flash(_('Media upload error (S3)'), 'error')
            raise
    else:
        upload_directory = os.path.join(DefaultConfig.CONTENT_DIR, directory)
        make_dir(upload_directory)
        file_path = os.path.join(upload_directory, file_name)
        try:
            uploaded_file.save(file_path)
        except:
            flash(_('Media upload error (filesystem)'), 'error')
            raise
        location = "{0}/{1}".format(directory, file_name)

    if process_audio:
        amplified_file_data = get_amplified_file(file_path, 0.0, True, True, None)
        if amplified_file_data[0]:
            location = "{0}/{1}".format(directory, amplified_file_data[1].split("/").pop())  # only UNIX safe!
    return location


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


def random_boolean(threshold):
    """returns 1 threshold percent of the time, otherwise 0"""
    r = random.random()
    if r > threshold:
        return 0
    else:
        return 1


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_AVATAR_EXTENSIONS


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    # return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# convert a form errors to an error dict for json display
def error_dict(form_errors):
    d = {}
    for (field, messages) in form_errors.items():
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
        for (k, v) in a.__dict__.items():
            # skip privates
            if k.startswith('_'):
                continue
            if k in named_dict:
                named_dict[k].append(v)
            else:
                named_dict[k] = [v]
    return named_dict


def fk_lookup_form_data(model_dict, data):
    """Checks to ensure all named models have an object with the specified id
    Takes a dict of model names and classes
    and form dict with fields and values

    Modifies form dict, replacing id int with object reference

    Returns JSON error dict if lookup error, False otherwise """
    for (field, cls) in model_dict.items():
        try:
            data[field] = cls.query.get(int(data[field]))
        except ValueError:
            response = {'status': 'error', 'errors': {field: _('Invalid ') + field}, 'status_code': 400}
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


def read_config(from_filename):
    """Reads config options from a file.
    Used for scheduler.cfg in app.py
    modified from https://gist.github.com/bennylope/2999704"""
    with open(from_filename) as f:
        content = f.read()

    config = {}
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9.]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            config[key] = val
    return config


class CustomJSONEncoder(json.JSONEncoder):
    """custom json encoder class that can handle python datetimes
    Drops microseconds, because Android client doesn't like it so precise"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return datetime.isoformat(obj.replace(microsecond=0))
        if isinstance(obj, time):
            return time.isoformat(obj.replace(microsecond=0))
        if isinstance(obj, timedelta):
            return str(obj)
        # add support for other serialization formats here...
        return super(CustomJSONEncoder, self).default(obj)


# monkey patch wtforms to allow field_order attribute
# from http://stackoverflow.com/a/18475322
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


# Poor man's paging
class Paginator():
    def get_json_datatable(self, processed_query, result_set, columns=None):
        datatable = dict()
        if columns is None:
            datatable['columns'] = []
            for column_description in processed_query.column_descriptions:
                datatable['columns'].append(column_description['name'])
        else:
            datatable['columns'] = columns

        datatable['data'] = []
        # results = processed_query.all()
        for row in result_set:
            datatable['data'].append(list(row))
        # datatable['recordsFiltered'] = len(results)
        return datatable

    def get_records(self, base_query, searchable_columns, request):
        # sorting
        base_query = base_query.order_by(
            text('{0} {1}'.format(base_query.column_descriptions[int(request.args['order[0][column]'])]['name'],
                             request.args['order[0][dir]'])))
        # searching
        filters = []
        for col in searchable_columns:
            filters.append(col.ilike('%{0}%'.format(request.args['search[value]'])))
        base_query = base_query.filter(or_(*filters))

        # paging
        result_set = base_query.slice(int(request.args['start']),
                                      int(request.args['start']) + int(request.args['length']))
        datatable = self.get_json_datatable(base_query, result_set)
        # sys.setrecursionlimit(10000)
        datatable['recordsTotal'] = datatable['recordsFiltered'] = len(
            base_query.all())  # base_query.count() should be used instead, but results in recursion depth error.
        # This implementation hits the db again, and retrieves the entire dataset just to count rows!!
        return datatable

    def get_records_from_query(self, query, request, columns):
        result_set = query.fetchall()
        datatable = self.get_json_datatable(query, result_set[
                                                   int(request.args['start']): int(request.args['start']) + int(
                                                       request.args['length'])],
                                            columns)  # wasteful, gets all records and just returns a
        # small size equal to the window
        datatable['recordsTotal'] = datatable['recordsFiltered'] = len(result_set)
        return datatable


# paginator
jquery_dt_paginator = Paginator()


def get_normalized_file(input_file, db_level=0):
    """
    wrapper for pySox norm command
    :param input_file: name of the input file to process
    :param db_level: the db level to which to normalize the audio file
    :return: Boolean of whether or not the process was successful
    """
    try:
        transformer = sox.Transformer()
        transformer.norm(db_level)
        input_file_parts = input_file.split('/')
        input_file_parts[len(input_file_parts) - 1] = "{0}_{1}_{2}".format("norm", db_level, input_file_parts[len(input_file_parts) - 1])
        output_file = '/'.join(input_file_parts)
        transformer.build(input_file, output_file)
        return True, output_file
    except:
        return False, input_file


def get_amplified_file(input_file, gain_db=0.0, normalize=True, limiter=True, balance=None):
    """
    Wrapper for PySox gain command
    :param input_file: name of the input file to process
    :param gain_db: The gain in db to be applied to the file
    :param normalize: Whether or not to apply normalization
    :param limiter: Whether or not to use a limiter to prevent clipping
    :param balance: Balance options. See docs on balance parameter for pysox:gain
    :return: Boolean of whether or not the process was successful
    """
    try:
        transformer = sox.Transformer()
        transformer.gain(gain_db, normalize, limiter, balance)
        input_file_parts = input_file.split('/')
        input_file_parts[len(input_file_parts) - 1] = "{0}_{1}_{2}".format("gain", gain_db, input_file_parts[len(input_file_parts) - 1])
        output_file = '/'.join(input_file_parts)
        transformer.build(input_file, output_file)
        return True, output_file
    except Exception as e:
        print e.message
        return False, input_file
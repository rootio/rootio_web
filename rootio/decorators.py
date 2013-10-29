# -*- coding: utf-8 -*-

from functools import wraps
from flask import json, abort, request, Response
from flask.ext.login import current_user
from flask_sqlalchemy import BaseQuery, Model

from .utils import simple_serialize_sqlalchemy

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_code != 0:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def returns_json(f):
    """takes either a sqlalchemy query or a dictionary w/ optional status_code
    returns a json response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        if isinstance(r,BaseQuery):
            obj_list = []
            for o in r.all():
                obj_list.append(simple_serialize_sqlalchemy(o))
            return Response(json.dumps(obj_list), content_type='application/json; charset=utf-8')
        if isinstance(r,Model):
            return Response(json.dumps(simple_serialize_sqlalchemy(r)), content_type='application/json; charset=utf-8')
        if isinstance(r,dict) and 'status_code' in r:
            return Response(json.dumps(r), content_type='application/json; charset=utf-8',status=r['status_code'])
        return Response(json.dumps(r), content_type='application/json; charset=utf-8')
    return decorated_function

def api_key_required(f):
    """Restrict access to a valid station api key """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from rootio.radio import Station
        api_key = request.args.get('api_key')
        if api_key:
            if 'station_id' in kwargs:
                station = Station.query.get(kwargs['station_id'])
                if station and station.api_key == api_key:
                    #valid
                    return f(*args, **kwargs)
            else:
                #no specific station, check against all valid keys
                if Station.query.filter_by(api_key=api_key).count():
                    #matches, should be only one because of unique constraint
                    return f(*args, **kwargs)
        abort(403)
    return decorated_function

#unfortunate duplication for flask-restless style preprocessor
#from flask.ext.restless import NO_CHANGE
from flask.ext.restless import ProcessingException
def restless_api_key_auth(*args, **kwargs):
    from rootio.radio import Station
    api_key = request.args.get('api_key')
    if api_key:
        if 'station_id' in kwargs:
            station = Station.query.get(kwargs['station_id'])
            if station and station.api_key == api_key:
                return None #no change
        else:
            #no specific station, check against all valid keys
            if Station.query.filter_by(api_key=api_key).count():
                return None #no change
    abort(403)

#define restless preprocessor dict for all method types
restless_api_key_required = dict(GET_SINGLE=[restless_api_key_auth],
                                GET_MANY=[restless_api_key_auth],
                                PATCH_SINGLE=[restless_api_key_auth],
                                PATCH_MANY=[restless_api_key_auth],
                                PUT_SINGLE=[restless_api_key_auth],
                                PUT_MANY=[restless_api_key_auth],
                                POST=[restless_api_key_auth],
                                DELETE=[restless_api_key_auth])

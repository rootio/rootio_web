# -*- coding: utf-8 -*-

from functools import wraps
import dateutil.parser

from flask import json, abort, request, Response
from flask.ext.login import current_user
from flask.ext.restless import ProcessingException

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
    returns a json response where collections are nested in an objects dict"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        ct = 'application/json; charset=utf-8'
        if isinstance(r,BaseQuery):
            obj_list = []
            for o in r.all():
                obj_list.append(simple_serialize_sqlalchemy(o))
            return Response(json.dumps({'objects':obj_list}), content_type=ct)
        if isinstance(r,list):
            obj_list = []
            for o in r:
                obj_list.append(simple_serialize_sqlalchemy(o))
            return Response(json.dumps({'objects':obj_list}), content_type=ct)
        if isinstance(r,Model):
            return Response(json.dumps(simple_serialize_sqlalchemy(r)), content_type=ct)
        if isinstance(r,dict) and 'status_code' in r:
            return Response(json.dumps(r), content_type=ct,status=r['status_code'])
        return Response(json.dumps(r), content_type=ct)
    return decorated_function

def returns_flat_json(f):
    """takes either a sqlalchemy query or a dictionary w/ optional status_code
    returns a json response where collections are in an array"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        ct = 'application/json; charset=utf-8'
        if isinstance(r,BaseQuery):
            obj_list = []
            for o in r.all():
                obj_list.append(simple_serialize_sqlalchemy(o))
            return Response(json.dumps(obj_list), content_type=ct)
        if isinstance(r,list):
            obj_list = []
            for o in r:
                obj_list.append(simple_serialize_sqlalchemy(o))
            return Response(json.dumps(obj_list), content_type=ct)
        if isinstance(r,Model):
            return Response(json.dumps(simple_serialize_sqlalchemy(r)), content_type=ct)
        if isinstance(r,dict) and 'status_code' in r:
            return Response(json.dumps(r), content_type=ct,status=r['status_code'])
        return Response(json.dumps(r), content_type=ct)
    return decorated_function

def api_key_or_auth_required(f):
    """Restrict access to a valid station api key, or logged in user """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from .radio import Station
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
        else:
            if current_user.is_authenticated():
                return f(*args, **kwargs)
        abort(403)
    return decorated_function

#unfortunate duplication for flask-restless style preprocessor

def restless_api_auth(*args, **kwargs):
    from .radio import Station
    api_key = request.args.get('api_key')
    if api_key:
        if 'station_id' in kwargs:
            station = Station.query.get(kwargs['station_id'])
            if station and station.api_key == api_key:
                return None # allow
        else:
            #no specific station, check against all valid keys
            if Station.query.filter_by(api_key=api_key).count():
                return None # allow
    else:
        #check if user is logged in
        if current_user.is_authenticated():
            return None # allow

    raise ProcessingException(message='Not authenticated!')
    

def since_filter(search_params=None, **kwargs):
    if 'since' in request.args:
        #parse iso datetime
        try:
            date = dateutil.parser.parse(request.args.get('since'))
        except (ValueError, TypeError):
            raise ProcessingException(message='Unable to parse since parameter. Must be ISO datetime format')

        #filter on update time
        filt = dict(name='updated_at', op='gt', val=date)
        if 'filters' not in search_params:
            search_params['filters'] = []
        search_params['filters'].append(filt)


def hide_private_variables(result=None, **kw):
    if hasattr(result, 'keys'):
        for key in result.keys():
            if key.startswith('_'):
                del result[key]
            if key in ["activation_key","openid","api_key"]:
                del result[key]

#define restless preprocessor dict for all method types
restless_preprocessors = { 'GET_SINGLE':   [restless_api_auth, since_filter],
                           'GET_MANY':     [restless_api_auth, since_filter],
                           'PATCH_SINGLE': [restless_api_auth, since_filter],
                           'PATCH_MANY':   [restless_api_auth, since_filter],
                           'PUT_SINGLE':   [restless_api_auth, since_filter],
                           'PUT_MANY':     [restless_api_auth, since_filter],
                           'POST':         [restless_api_auth, since_filter],
                           'DELETE':       [restless_api_auth, since_filter]}
restless_postprocessors = {
    'GET_SINGLE':   [hide_private_variables],
    'GET_MANY':     [hide_private_variables]
}
# -*- coding: utf-8 -*-

from functools import wraps
from flask import json, abort, Response
from flask.ext.login import current_user
from flask_sqlalchemy import BaseQuery

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
            #serialize query in simplist way possible, no joins
            instance = r.first() #need an instance of the query to get keys
            if not instance:
                return Response(json.dumps([]), content_type='application/json; charset=utf-8')
            keys = [k for k in instance.__dict__.keys() if not k.startswith('_')] #gets non-private keys, ignore relations
            obj_list = r.all() #evaluate list
            serial_list = [{col: getattr(d, col) for col in keys} for d in obj_list]
            return Response(json.dumps(serial_list), content_type='application/json; charset=utf-8')
        if isinstance(r,dict) and 'status_code' in r:
            return Response(json.dumps(r), content_type='application/json; charset=utf-8',status=r['status_code'])
        return Response(json.dumps(r), content_type='application/json; charset=utf-8')
    return decorated_function

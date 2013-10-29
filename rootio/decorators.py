# -*- coding: utf-8 -*-

from functools import wraps
from flask import json, abort, Response
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

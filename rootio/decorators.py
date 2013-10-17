# -*- coding: utf-8 -*-

from functools import wraps
from flask import json, abort, Response
from flask.ext.login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_code != 0:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        if 'status_code' in r:
            return Response(json.dumps(r), content_type='application/json; charset=utf-8',status=r['status_code'])
        return Response(json.dumps(r), content_type='application/json; charset=utf-8')
    return decorated_function

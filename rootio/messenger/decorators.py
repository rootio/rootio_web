from functools import wraps

from flask import current_app
from ..utils import CustomJSONEncoder

def sends_json(f):
    """Takes a tuple (topic, message) and sends it as json to the scheduler,
    which will pass it at the appointed time to telephony_server"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        (topic, msg) = f(*args, **kwargs)
        m = "%s %s" % (topic, msg)
	current_app.messenger.send(topic, msg)
    return decorated_function

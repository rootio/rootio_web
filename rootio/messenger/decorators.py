from functools import wraps

from flask import current_app
from ..utils import CustomJSONEncoder


def sends_multipart(f):
    """Takes a tuple (topic, message) and sends it to the scheduler,
    which will pass it at the appointed time to telephony_server"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        topic, msg = f(*args, **kwargs)
		msg = json.dumps(d, cls=CustomJSONEncoder)
        current_app.messenger.send_multipart((topic, msg))
    return decorated_function

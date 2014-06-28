import datetime
import dateutil.parser

__author__ = 'kenneth'


def update_tz(time, offset):
    if offset < 0:
        result = dateutil.parser.parse(time) - datetime.timedelta(minutes=offset*-1)
    elif offset > 0:
        result = dateutil.parser.parse(time) + datetime.timedelta(minutes=offset)
    else:
        result = dateutil.parser.parse(time)
    return result

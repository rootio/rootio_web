import isodate

def parse_datetime(parameter):
    "Parses a URL parameter formatted in isoformat"
    if parameter:
        try:
            return isodate.parse_datetime(parameter)
        except ValueError:
            pass
    return None

import dateutil.parser

def parse_datetime(parameter):
    "Parses a URL parameter formatted in isoformat"
    if parameter:
        try:
            return dateutil.parser.parse(parameter)
        except ValueError:
            pass
    return None

   
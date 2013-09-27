from sqlalchemy import types, String
from wtforms_components.fields import TimeField
from wtforms_components.widgets import TimeInput

class FileField(types.TypeDecorator):
    impl = String

    def __init__(self, upload_set, *args, **kwargs):
        super(FileField, self).__init__(*args, **kwargs)
        self.upload_set = upload_set

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.filename
        return value

    def process_result_value(self, value, dialect):
        return FileNameString(self.upload_set, value)


class FileNameString(object):

    def __init__(self, upload_set, filename):
        self.upload_set = upload_set
        self.filename = filename

    def save(self, req_file):
        self.filename = self.upload_set.save(req_file)
        return self.filename

    @property
    def url(self):
        return self.upload_set.url(self.filename)

class DurationField(TimeField):
    widget = TimeInput(step='1')
    error_msg = 'Not a valid duration.'

    #because this is rendered as an html5 input, format depends on browser locale
    #TODO: investigate using textfield with custom pattern instead

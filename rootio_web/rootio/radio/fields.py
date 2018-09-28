from sqlalchemy import types, String
from wtforms.fields import FormField
from wtforms import StringField, TextAreaField
from wtforms_components.widgets import TextInput

import json


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


class DurationField(StringField):
    widget = TextInput(pattern="^(0*[0-9]|1[0-9]|2[0-3])([.:][0-5][0-9])([.:][0-5][0-9])?$")
    error_msg = 'Not a valid duration.'

    # html5 time inputs include am/pm, which doesn't make sense for duration
    # use textfield with custom pattern instead
    # matches (H)H.:MM(.:SS)


class InlineFormField(FormField):
    def validate(self, form, extra_validators=tuple()):
        # don't validate inline form fields, we'll do it client side
        return True

    def populate_obj(self, obj, name):
        # don't populate inline forms
        return True


class JSONField(TextAreaField):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        else:
            return self.data and unicode(json.dumps(self.data)) or u''

    def process_formdata(self, value):
        if value:
            try:
                self.data = json.loads(value[0])
            except ValueError:
                raise ValueError(self.gettext(u'Invalid JSON data.'))

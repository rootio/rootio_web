from wtforms import TextAreaField
import json

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
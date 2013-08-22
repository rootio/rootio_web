from sqlalchemy import types, String

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
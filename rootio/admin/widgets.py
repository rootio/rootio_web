from wtforms.widgets import HTMLString, html_params
from cgi import escape
import six
from wtforms.fields import Field


class ParagraphWidget(object):
    """
    Renders a field as a plain ol' paragraph
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return HTMLString(
            '<p %s>%s</p>' % (html_params(name=field.name, **kwargs), escape(six.text_type(field._value()))))


class DateDisplayOnlyField(Field):
    """
    A field that is not editable. No way, no how.
    """
    widget = ParagraphWidget()

    def _value(self):
        return self.data

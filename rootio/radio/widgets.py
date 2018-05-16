from wtforms.widgets import Select


class ChoicesSelect(Select):
    """A Select field that we can pass a list of choices to constrain input"""
    def __init__(self, multiple=False, choices=()):
        self.choices = choices
        super(ChoicesSelect, self).__init__(multiple)

    def __call__(self, field, **kwargs):
        field.iter_choices = lambda: ((val, label, val == field.default) 
                                      for val, label in self.choices)
        return super(ChoicesSelect, self).__call__(field, **kwargs)
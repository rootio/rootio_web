# fake validator to set field has_inline_form
class HasInlineForm(object):
    field_flags = ('has_inline_form',)  # if True, render macro will look for a FormField with {{field.name}}_inline

    def __init__(self, value, message=None):
        self.message = message

    def __call__(self, form, field):
        return True

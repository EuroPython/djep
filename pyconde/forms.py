from crispy_forms import layout
from crispy_forms.utils import render_field


class Submit(layout.Submit):
    field_classes = 'submit'
    tabindex = None

    def __init__(self, *args, **kwargs):
        super(Submit, self).__init__(*args, **kwargs)
        if 'tabindex' in kwargs:
            self.tabindex = kwargs['tabindex']


class ExtendedHelpField(layout.Field):
    """
    Renders like a normal field but the help text is only wrapped inside a
    div to allow for some more complex HTML in there. As second argument the
    constructor accepts the optional extended help text.
    """
    template = 'crispy_addons/extended-help-field.html'

    def __init__(self, field, help, *args, **kwargs):
        self.help = help
        super(ExtendedHelpField, self).__init__(field, *args, **kwargs)

    def render(self, form, form_style, context):
        context.update({'extended_help': self.help})
        return render_field(self.field, form, form_style, context, template=self.template, attrs=self.attrs)

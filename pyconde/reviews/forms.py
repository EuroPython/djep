from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

from . import models


class UpdateProposalForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)
    abstract = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(UpdateProposalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('title', autofocus='autofocus'),
            Field('description'),
            Field('abstract'),
            ButtonHolder(Submit('save', "Speichern", css_class="btn-primary"))
            )

    @classmethod
    def init_from_proposal(cls, proposal):
        form = cls(initial={
            'title': proposal.title,
            'description': proposal.description,
            'abstract': proposal.abstract
            })
        return form


class CommentForm(forms.ModelForm):
    class Meta(object):
        model = models.Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('content'),
            ButtonHolder(Submit('comment', "Kommentar abschicken", css_class='btn btn-primary'))
            )

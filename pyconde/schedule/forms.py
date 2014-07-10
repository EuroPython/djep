# -*- encoding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

from . import models


class EditSessionForm(forms.ModelForm):
    class Meta(object):
        model = models.Session
        fields = ('abstract', 'description',)

    def __init__(self, *args, **kwargs):
        super(EditSessionForm, self).__init__(*args, **kwargs)
        self.fields['abstract'].label = ugettext("Abstract")
        self.fields['description'].label = ugettext("Description")
        self.fields['abstract'].help_text = ugettext("""This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> as input.""")
        self.fields['description'].help_text = ugettext("""This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> as input.""")
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Field('abstract'),
            Field('description'),
            ButtonHolder(Submit('save', _("Save"), css_class="btn btn-primary"))
            )


class EditSessionCoverageForm(forms.ModelForm):
    class Meta:
        model = models.Session
        fields = ['slides_url', 'video_url']

    def __init__(self, *args, **kwargs):
        super(EditSessionCoverageForm, self).__init__(*args, **kwargs)
        self.fields['slides_url'].label = 'URL zu den Folien'
        self.fields['video_url'].label = 'URL zum Video'
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Field('slides_url'),
            Field('video_url'),
            ButtonHolder(Submit('save', _("Save"), css_class="btn btn-primary"))
        )

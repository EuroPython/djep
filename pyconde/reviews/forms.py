# -*- coding: UTF-8 -*-
from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, HTML

from . import models
from pyconde.proposals import forms as proposal_forms


class UpdateProposalForm(forms.Form):
    title = forms.CharField(label="Titel", max_length=255)
    description = forms.CharField(label="Beschreibung", widget=forms.Textarea)
    abstract = forms.CharField(label="Abstract", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(UpdateProposalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
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


class UpdateTalkProposalForm(UpdateProposalForm):
    def __init__(self, *args, **kwargs):
        super(UpdateTalkProposalForm, self).__init__(*args, **kwargs)
        proposal_forms.TalkSubmissionForm().customize_fields(form=self)


class UpdateTutorialProposalForm(UpdateProposalForm):
    def __init__(self, *args, **kwargs):
        super(UpdateTutorialProposalForm, self).__init__(*args, **kwargs)
        proposal_forms.TutorialSubmissionForm().customize_fields(form=self)


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


class ReviewForm(forms.ModelForm):
    class Meta(object):
        model = models.Review
        fields = ['rating', 'summary']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('rating'), Field('summary'),
            ButtonHolder(Submit('save', "Review abgeben", css_class='btn-primary')))


class UpdateReviewForm(ReviewForm):
    def __init__(self, *args, **kwargs):
        super(UpdateReviewForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('rating'), Field('summary'),
            ButtonHolder(
                HTML(u"""<a href="{0}">Löschen</a>""".format(
                    reverse('reviews-delete-review',
                        kwargs={'pk': kwargs.get('instance').proposal.pk}))),
                Submit('save', "Änderungen speichern", css_class='btn-primary')
                )
            )

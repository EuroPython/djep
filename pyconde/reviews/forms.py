# -*- coding: UTF-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, HTML, Fieldset, Button

from taggit.utils import edit_string_for_tags

from . import models
from pyconde.proposals import forms as proposal_forms
from pyconde.conference import models as conference_models
from pyconde.forms import Submit


class UpdateProposalForm(forms.ModelForm):

    class Meta(object):
        model = models.ProposalVersion
        fields = [
            'title', 'abstract', 'description', 'duration', 'audience_level',
            'tags', 'language',
        ]

    def __init__(self, *args, **kwargs):
        self.kind_instance = kwargs.pop('kind_instance', None)
        super(UpdateProposalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('title', autofocus='autofocus'),
                Field('abstract'),
                Field('description'),
                ),
            Fieldset(_('Details'),
                Field('duration'),
                Field('audience_level'),
                Field('tags'),
                Field('language'),
                ),
            ButtonHolder(Submit('save', _("Save"), css_class="btn-primary"))
            )

    def save(self, commit=True):
        instance = super(UpdateProposalForm, self).save(False)
        self.customize_save(instance)
        if commit:
            instance.save()
        return instance

    def customize_save(self, instance):
        """
        This is executed right after the initial save step to enforce
        some values no matter what was previously assigned to this form.
        """
        pass

    @classmethod
    def init_from_proposal(cls, proposal):
        # Right now this code smells a bit esp. with regards to tags
        form = cls(initial={
            'title': proposal.title,
            'abstract': proposal.abstract,
            'description': proposal.description,
            'tags': edit_string_for_tags(proposal.tags.all()),
            'language': proposal.language,
            'speaker': proposal.speaker,
            'additional_speakers': proposal.additional_speakers.all(),
            'track': proposal.track,
            'duration': proposal.duration,
            'audience_level': proposal.audience_level,
            'available_timeslots': proposal.available_timeslots.all(),
        }, kind_instance=proposal.kind)
        return form


class UpdateTalkProposalForm(UpdateProposalForm):
    def __init__(self, *args, **kwargs):
        super(UpdateTalkProposalForm, self).__init__(*args, **kwargs)
        proposal_forms.TalkSubmissionForm().customize_fields(form=self)
        # Since track is available in the original proposal form, we have
        # to delete it here explicitly.
        del self.fields['track']


class UpdateTutorialProposalForm(UpdateProposalForm):
    class Meta(object):
        model = models.ProposalVersion
        fields = ['title', 'abstract', 'description', 'audience_level', 'tags']

    def __init__(self, *args, **kwargs):
        super(UpdateTutorialProposalForm, self).__init__(*args, **kwargs)
        proposal_forms.TutorialSubmissionForm().customize_fields(form=self)
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('title', autofocus='autofocus'),
                Field('abstract'),
                Field('description'),
                ),
            Fieldset(_('Details'),
                Field('audience_level'),
                Field('tags'),
                ),
            ButtonHolder(Submit('save', _("Save"), css_class="btn-primary"))
            )

    def customize_save(self, instance):
        instance.duration = conference_models.SessionDuration.current_objects.get(slug='tutorial')


class CommentForm(forms.ModelForm):
    class Meta(object):
        model = models.Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('content'),
            ButtonHolder(Submit('comment', _("Send feedback"), css_class='btn btn-primary comment'))
            )


class ReviewForm(forms.ModelForm):
    class Meta(object):
        model = models.Review
        fields = ['rating', 'summary']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Field('rating'), Field('summary'),
            ButtonHolder(Submit('save', _("Save review"), css_class='btn-primary btn save')))


class UpdateReviewForm(ReviewForm):
    def __init__(self, *args, **kwargs):
        super(UpdateReviewForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('rating', autofocus="autofocus", tabindex=1), Field('summary', tabindex=2),
            ButtonHolder(
                HTML(u"""<a tabindex="4" class="btn" href="{0}"><i class="fa fa-fw fa-times"></i> {1}</a>""".format(
                    reverse('reviews-delete-review',
                        kwargs={'pk': kwargs.get('instance').proposal.pk}),
                    _("Delete"))),
                Submit('save', _("Save changes"), css_class='btn-primary btn save', tabindex=3)
                )
            )


class ProposalFilterForm(forms.Form):
    track = forms.ChoiceField(widget=forms.Select, required=False)
    kind = forms.ChoiceField(widget=forms.Select, required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalFilterForm, self).__init__(*args, **kwargs)
        self.fields['track'].choices = [('', ugettext('Track')), ('-', '----------')] + [(t.slug, t.name) for t in conference_models.Track.objects.all()]
        self.fields['kind'].choices = [('', ugettext('Session type')), ('-', '----------')] + [(t.slug, t.name) for t in conference_models.SessionKind.objects.exclude(slug='keynote').all()]

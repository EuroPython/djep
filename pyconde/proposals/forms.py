# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Fieldset, Submit, Field, HTML
from pyconde.forms import ExtendedHelpField

from pyconde.conference.models import current_conference
from pyconde.conference import models as conference_models
from pyconde.speakers import models as speaker_models

from . import models
from . import settings
from . import validators


class HiddenSpeakersMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        """
        Basically any speaker id is valid.
        """
        speakers = speaker_models.Speaker.objects.filter(pk__in=value)
        if len(speakers) != len(value):
            raise ValidationError(self.error_messages['invalid_choice'] % value)
        return speakers


class ProposalSubmissionForm(forms.ModelForm):

    class Meta(object):
        model = models.Proposal
        fields = [
            "kind",
            "title",
            "abstract",
            "description",
            "additional_speakers",
            "audience_level",
            "duration",
            "track",
            "tags",
            "available_timeslots",
            "language",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        self.kind_instance = kwargs.pop('kind_instance', None)
        super(ProposalSubmissionForm, self).__init__(*args, **kwargs)
        tracks = conference_models.Track.current_objects.all()
        self.customize_fields(form=None, tracks=tracks, instance=kwargs.get('instance', None))

        instance = kwargs.get('instance')
        if instance:
            button_text = _("Save changes")
        else:
            button_text = _("Submit proposal")
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('kind', autofocus="autofocus"),
                Field('title'),
                Field('abstract'),
                Field('description'),
                Field('agree_to_terms')),
            Fieldset(_('Details'),
                Field('language'),
                Field('available_timeslots'),
                # ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})),
                Field('track'),
                Field('tags'),
                Field('duration'),
                Field('audience_level'),
                Field('additional_speakers', css_class='multiselect-user'),
                Field('notes')),
            ButtonHolder(
                Submit('submit', button_text, css_class="btn btn-primary"))
        )

    def customize_fields(self, instance=None, form=None, tracks=None):
        if form is None:
            form = self
        if tracks is None:
            tracks = conference_models.Track.current_objects.all()
        if not settings.SUPPORT_ADDITIONAL_SPEAKERS:
            del form.fields['additional_speakers']
        else:
            # Only list already selected speakers or an empty queryset
            if instance is not None:
                additional_speakers = instance.additional_speakers.all()
            else:
                additional_speakers = speaker_models.Speaker.objects.none()
            form.fields['additional_speakers'] = HiddenSpeakersMultipleChoiceField(label=_("Additional speakers"),
                queryset=additional_speakers, required=False)
        if 'kind' in self.fields:
            form.fields['kind'] = forms.ModelChoiceField(label=_("Type"),
                queryset=conference_models.SessionKind.current_objects.filter_open_kinds())
        if 'audience_level' in self.fields:
            form.fields['audience_level'] = forms.ModelChoiceField(label=_("Target-audience"),
                queryset=conference_models.AudienceLevel.current_objects.all())
        if 'duration' in self.fields:
            form.fields['duration'] = forms.ModelChoiceField(label=_("Duration"),
                queryset=conference_models.SessionDuration.current_objects.all())
        if 'track' in self.fields:
            form.fields['track'] = forms.ModelChoiceField(label=_("Track"), required=True, initial=None,
                queryset=tracks)
        if 'abstract' in self.fields:
            form.fields['abstract'].help_text = _("""Up to around 50 words. Appears in the printed program. <br />This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> input.""")
            # form.fields['abstract'].validators = [validators.MaxLengthValidator(3000)]
        if 'description' in form.fields:
            form.fields['description'].help_text = _("""Describe your presentation in detail. This is what will be reviewed during the review phase.<br />This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> input.""")
            # form.fields['description'].validators = [validators.MaxLengthValidator(2000)]
        if 'additional_speakers' in form.fields:
            form.fields['additional_speakers'].help_text = _("""If you want to present with others, please enter their names here.""")
        if 'available_timeslots' in form.fields:
            form.fields['available_timeslots'] = forms.ModelMultipleChoiceField(
                label=_("Available timeslots"),
                queryset=models.TimeSlot.objects.select_related('section').filter(section__conference=conference_models.current_conference()).order_by('date', 'slot'),
                widget=forms.CheckboxSelectMultiple,
                required=False
            )
            form.fields['available_timeslots'].help_text += ugettext(
                """<br /><br />Please pick all the times that should be considered for your """
                """presentation/training. If possible these will be used for the final timeslot.""")
        if 'notes' in form.fields:
            form.fields['notes'].help_text = _(
                """Add notes or comments here that can only be seen by reviewers and the organizing team.""")
        if 'accept_recording' in form.fields:
            form.fields['accept_recording'].label =_(
                """I agree to allow the Python Software Verband e.V. to record my presentation on EuroPython 2014 in Berlin.""")
        if 'language' in form.fields:
            form.fields['language'].initial = settings.DEFAULT_LANGUAGE

    def clean(self):
        cleaned_data = super(ProposalSubmissionForm, self).clean()
        kind = cleaned_data.get('kind')
        if kind is not None and not kind.accepts_proposals():
            raise forms.ValidationError(_("The selected session type is no longer accepting proposals."))
        return cleaned_data

    def clean_audience_level(self):
        value = self.cleaned_data["audience_level"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid target-audience."))
        return value

    def clean_duration(self):
        value = self.cleaned_data["duration"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid duration."))
        return value

    def clean_kind(self):
        value = self.cleaned_data["kind"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid session type."))
        return value


class TypedSubmissionForm(ProposalSubmissionForm):
    """
    Base class for all typed submission forms. It removes the kind field from
    the form and sets it according the session kind provided by the view.
    """
    class Meta(object):
        model = models.Proposal
        fields = [
            "title",
            "abstract",
            "description",
            "additional_speakers",
            "audience_level",
            "tags",
            "track",
            "duration",
            "available_timeslots",
            "language",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super(TypedSubmissionForm, self).__init__(*args, **kwargs)
        tracks = conference_models.Track.current_objects.all()
        instance = kwargs.get('instance')
        if instance:
            button_text = _("Save changes")
        else:
            button_text = _("Submit proposal")
            # Also select all available timeslots by default
            if 'available_timeslots' in self.fields:
                self.initial['available_timeslots'] = [ts.pk for ts in self.fields['available_timeslots'].queryset]
        self.helper.layout = Layout(
            Fieldset(_('General'),
                     Field('title', autofocus="autofocus"),
                     Field('abstract'),
                     Field('description')),
            Fieldset(_('Details'),
                     Field('language'),
                     Field('available_timeslots'),
                     # ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})),
                     Field('track'),
                     Field('tags'),
                     Field('duration'),
                     Field('audience_level'),
                     Field('additional_speakers', css_class='multiselect-user'),
                     Field('notes')),
            ButtonHolder(
                Submit('submit', button_text, css_class="btn btn-primary"))
        )

    def customize_fields(self, instance=None, form=None, tracks=None):
        super(TypedSubmissionForm, self).customize_fields(instance, form, tracks)
        if form is None:
            form = self
        if 'available_timeslots' in form.fields and \
                form.kind_instance is not None:
            form.fields['available_timeslots'].queryset = form.fields['available_timeslots'] \
                .queryset.filter(section__in=form.kind_instance.sections.all())

    def save(self, commit=True):
        instance = super(TypedSubmissionForm, self).save(False)
        instance.kind = self.kind_instance
        self.customize_save(instance)
        if commit:
            instance.save()
        return instance

    def customize_save(self, instance):
        pass


class TrainingSubmissionForm(TypedSubmissionForm):
    class Meta(object):
        model = models.Proposal
        fields = [
            "title",
            "description",
            "abstract",
            "additional_speakers",
            "audience_level",
            "tags",
            "available_timeslots",
            "language",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super(TrainingSubmissionForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            button_text = _("Save changes")
        else:
            button_text = _("Submit training")
        self.helper.layout = Layout(
            Fieldset(
                _('General'),
                Field('title', autofocus="autofocus"),
                Field('description'),
                Field('abstract')),
            Fieldset(
                _('Details'),
                Field('language'),
                Field('available_timeslots'),
                Field('tags'),
                Field('audience_level'),
                Field('additional_speakers', css_class='multiselect-user'),
                Field('notes')),
            ButtonHolder(
                Submit('submit', button_text, css_class="btn btn-primary")),
        )

    def customize_fields(self, instance=None, form=None, tracks=None):
        super(TrainingSubmissionForm, self).customize_fields(instance, form, tracks)
        if form is None:
            form = self
        form.fields['description'].label = _("Description")
        form.fields['description'].validators.append(validators.MaxWordsValidator(300))
        form.fields['description'].help_text = ugettext(
            """This field supports <a href="http://daringfireball.net/projects/markdown/syntax" """
            """target="_blank" rel="external">Markdown</a> input.""") + ugettext(
            """<br />< 300 words""")
        form.fields['abstract'].label = _("Structure")
        form.fields['abstract'].help_text = ugettext(
            """This field supports <a href="http://daringfireball.net/projects/markdown/syntax" """
            """target="_blank" rel="external">Markdown</a> input.""") + ugettext(
            """<br /><br />Please provide details about the structure including the timing. The """
            """sum of these structural points has to be 180 minutes. Please also list any software """
            """(incl. version information) that attendees should install beforehand. The training """
            """examples should work on Linux, Mac OSX and Windows. If they don't, please mark them accordingly.""")

    def customize_save(self, instance):
        instance.duration = conference_models.SessionDuration.current_objects.get(slug='training')


class TalkSubmissionForm(TypedSubmissionForm):

    class Meta(object):
        model = models.Proposal
        fields = [
            "title",
            "abstract",
            "description",
            "additional_speakers",
            "audience_level",
            "tags",
            "track",
            "duration",
            "available_timeslots",
            "language",
            "notes",
            "accept_recording",
        ]

    def __init__(self, *args, **kwargs):
        super(TalkSubmissionForm, self).__init__(*args, **kwargs)
        record_fs = Fieldset(_('Video recording'),
            HTML(_('{% load cms_tags %}<p class="control-group">EuroPython talks are recorded on video. '
                   'Due to data protection regulations you need to explicitly accept our '
                   '<a href="{% page_url "privacy-policy" %}">privacy policy</a>. If you cannot agree to '
                   'your talk being recorded, please elaborate in the “Notes” above.</p>')),
            Field('accept_recording')
        )
        self.helper.layout.fields.insert(-1, record_fs)

    def customize_fields(self, instance=None, form=None, tracks=None):
        super(TalkSubmissionForm, self).customize_fields(instance, form, tracks)
        if form is None:
            form = self
        form.fields['duration'] = forms.ModelChoiceField(label=_("Duration"),
                queryset=conference_models.SessionDuration.current_objects.exclude(slug='talk').all())


class PosterSubmissionForm(TypedSubmissionForm):
    class Meta(object):
        model = models.Proposal
        fields = [
            "title",
            "abstract",
            "description",
            "additional_speakers",
            "tags",
            "track",
            "language",
            "notes",
        ]

    def customize_save(self, instance):
        instance.audience_level = conference_models.AudienceLevel.\
            current_objects.get(slug='novice')
        instance.duration = conference_models.SessionDuration.\
            current_objects.get(slug='poster')

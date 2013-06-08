# -*- encoding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
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
            "description",
            "abstract",
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
        super(ProposalSubmissionForm, self).__init__(*args, **kwargs)
        tracks = conference_models.Track.current_objects.all()
        self.customize_fields(form=None, tracks=tracks, instance=kwargs.get('instance', None))

        instance = kwargs.get('instance')
        if instance:
            button_text = u"Änderungen speichern"
        else:
            button_text = u"Vortrag einreichen"
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('kind', autofocus="autofocus"),
                'title',
                Field('description'),
                Field('abstract'),
                'agree_to_terms'),
            Fieldset(_('Details'),
                'language',
                'available_timeslots',
                ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})),
                'tags',
                'duration',
                'audience_level',
                Field('additional_speakers', css_class='multiselect-user'),
                'notes'),
            ButtonHolder(Submit('submit', button_text, css_class="btn-primary"))
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
            form.fields['additional_speakers'] = HiddenSpeakersMultipleChoiceField(label=_("additional speakers"),
                queryset=additional_speakers, required=False)
        if 'kind' in self.fields:
            form.fields['kind'] = forms.ModelChoiceField(label=_("kind"),
                queryset=conference_models.SessionKind.current_objects.filter_open_kinds())
        if 'audience_level' in self.fields:
            form.fields['audience_level'] = forms.ModelChoiceField(label=_("audience level"),
                queryset=conference_models.AudienceLevel.current_objects.all())
        if 'duration' in self.fields:
            form.fields['duration'] = forms.ModelChoiceField(label=_("duration"),
                queryset=conference_models.SessionDuration.current_objects.all())
        if 'track' in self.fields:
            form.fields['track'] = forms.ModelChoiceField(label=_("Track"), required=True, initial=None,
                queryset=tracks)
        if 'description' in form.fields:
            form.fields['description'].help_text = """Bis ca. 50 Worte. Erscheint im gedruckten Programm. <br />Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>."""
            form.fields['description'].validators = [validators.MaxLengthValidator(2000)]
        if 'abstract' in self.fields:
            form.fields['abstract'].help_text = """Darstellung des Vortragsinhalts und ist die Grundlage für das Review.<br />Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>."""
            form.fields['abstract'].validators = [validators.MaxLengthValidator(3000)]
        if 'additional_speakers' in form.fields:
            form.fields['additional_speakers'].help_text = """Wenn Sie den Vortrag zusammen mit anderen Personen halten wollen, tragen Sie hier bitte deren Namen ein."""
        if 'available_timeslots' in form.fields:
            form.fields['available_timeslots'] = forms.ModelMultipleChoiceField(
                label=_("available timeslots"),
                queryset=models.TimeSlot.objects.select_related('section').filter(section__conference=conference_models.current_conference()).order_by('date', 'slot'),
                widget=forms.CheckboxSelectMultiple,
                required=False
            )
            form.fields['available_timeslots'].help_text += u"""<br /><br />Bitte geben Sie hier alle Zeiten an, die für Ihren Vortrag/Ihr Tutorial in Frage kommen. Diese Zeiten werden dann so gut wie möglich für die Erstellung des Zeitplans in Betracht gezogen."""
        if 'notes' in form.fields:
            form.fields['notes'].help_text = u"""Hier können Sie Anmerkungen und Kommentare eintragen, die nur für die Reviewer und Organisatoren sichtbar sind."""

    def clean(self):
        cleaned_data = super(ProposalSubmissionForm, self).clean()
        kind = cleaned_data.get('kind')
        if kind is not None and not kind.accepts_proposals():
            raise forms.ValidationError(_("The selected session kind doesn't accept any proposals anymore."))
        return cleaned_data

    def clean_audience_level(self):
        value = self.cleaned_data["audience_level"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid audience level."))
        return value

    def clean_duration(self):
        value = self.cleaned_data["duration"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid duration."))
        return value

    def clean_kind(self):
        value = self.cleaned_data["kind"]
        if value.conference != current_conference():
            raise forms.ValidationError(_("Please select a valid session kind."))
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
            "description",
            "abstract",
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
            button_text = u"Änderungen speichern"
        else:
            button_text = u"Vortrag einreichen"
            # Also select all available timeslots by default
            if 'available_timeslots' in self.fields:
                self.initial['available_timeslots'] = [ts.pk for ts in self.fields['available_timeslots'].queryset]
        self.helper.layout = Layout(
            Fieldset(_('General'),
                     Field('title', autofocus="autofocus"),
                     Field('description'),
                     Field('abstract')),
            Fieldset(_('Details'),
                     'language',
                     'available_timeslots',
                     ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})),
                     'tags', 'duration', 'audience_level', Field('additional_speakers', css_class='multiselect-user'),
                     'notes'),
            ButtonHolder(Submit('submit', button_text, css_class="btn-primary"))
        )

    def save(self, commit=True):
        instance = super(TypedSubmissionForm, self).save(False)
        instance.kind = self.kind_instance
        self.customize_save(instance)
        if commit:
            instance.save()
        return instance

    def customize_save(self, instance):
        pass


class TutorialSubmissionForm(TypedSubmissionForm):
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
        super(TutorialSubmissionForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            button_text = u"Änderungen speichern"
        else:
            button_text = u"Tutorial einreichen"
        self.helper.layout = Layout(
            Fieldset(
                _('General'),
                Field('title', autofocus="autofocus"),
                Field('description'),
                Field('abstract')),
            Fieldset(
                _('Details'),
                'language', 'available_timeslots', 'tags', 'audience_level',
                Field('additional_speakers', css_class='multiselect-user'),
                'notes'),
            ButtonHolder(Submit('submit', button_text, css_class="btn-primary")),
        )

    def customize_fields(self, instance=None, form=None, tracks=None):
        super(TutorialSubmissionForm, self).customize_fields(instance, form, tracks)
        if form is None:
            form = self
        form.fields['description'].label = "Kurzbeschreibung"
        form.fields['description'].validators.append(validators.MaxWordsValidator(300))
        form.fields['description'].help_text = """Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>.<br />< 300 Worte"""
        form.fields['abstract'].label = "Gliederung"
        form.fields['abstract'].help_text = """Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>.<br /><br />
                                              Bitte stichpunktartige Angaben zum Aufbau des Tutorials mit Zeitangaben
                                              zu den einzelnen Punkten, wobei die Summe 180 Minuten ergeben muss.
                                              Bitte die benötigen Software-Pakete aufführen, so dass die Teilnehmer
                                              bereits vor dem Tutorial ihre Laptops einrichten können. Bitte Anforderungen
                                              an Versionen angeben und deren Zusammenspiel überprüfen.<br /><br /> Grundsätzlich
                                              sollten die Tutorial-Inhalte auf allen drei gängigen
                                              Betriebssystemen (Linux, Mac OS X und Windows) funktionieren.
                                              Wenn nicht, bitte explizit darauf hinweisen."""
        form.fields['available_timeslots'].queryset = form.fields['available_timeslots'].queryset.filter(section__slug='tutorials')

    def customize_save(self, instance):
        instance.duration = conference_models.SessionDuration.current_objects.get(slug='tutorial')


class TalkSubmissionForm(TypedSubmissionForm):
    def __init__(self, *args, **kwargs):
        super(TalkSubmissionForm, self).__init__(*args, **kwargs)
        self.helper.layout.fields.insert(-1, Fieldset('Videoaufzeichnung', HTML(u"""<p class="control-group">Optional können Vorträge auch aufgezeichnet werden. Es liegt während der Konferenz ein Papierformular auf, durch das Sie einer solchen Aufzeichnung zustimmen können. Mehr Informationen dazu finden Sie <a href="/vortragende/">hier</a>.</p>""")))

    def customize_fields(self, instance=None, form=None, tracks=None):
        super(TalkSubmissionForm, self).customize_fields(instance, form, tracks)
        if form is None:
            form = self
        form.fields['duration'] = forms.ModelChoiceField(label=_("duration"),
                queryset=conference_models.SessionDuration.current_objects.exclude(slug='tutorial').all())
        if 'available_timeslots' in form.fields:
            form.fields['available_timeslots'].queryset = form.fields['available_timeslots']\
                .queryset.filter(section__slug='konferenz')

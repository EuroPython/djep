# -*- encoding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Fieldset, Submit, Field, HTML
from pyconde.forms import ExtendedHelpField

from conference.models import current_conference
from conference import models as conference_models
from speakers import models as speaker_models

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
        ]

    def __init__(self, *args, **kwargs):
        super(ProposalSubmissionForm, self).__init__(*args, **kwargs)
        if not settings.SUPPORT_ADDITIONAL_SPEAKERS:
            del self.fields['additional_speakers']
        else:
            # Only list already selected speakers or an empty queryset
            if 'instance' in kwargs and kwargs['instance'] is not None:
                additional_speakers = kwargs['instance'].additional_speakers.all()
            else:
                additional_speakers = speaker_models.Speaker.objects.none()
            self.fields['additional_speakers'] = HiddenSpeakersMultipleChoiceField(label=_("additional speakers"),
                queryset=additional_speakers, required=False)
        tracks = conference_models.Track.current_objects.all()
        if 'kind' in self.fields:
            self.fields['kind'] = forms.ModelChoiceField(label=_("kind"),
                queryset=conference_models.SessionKind.current_objects.filter_open_kinds())
        if 'audience_level' in self.fields:
            self.fields['audience_level'] = forms.ModelChoiceField(label=_("audience level"),
                queryset=conference_models.AudienceLevel.current_objects.all())
        if 'duration' in self.fields:
            self.fields['duration'] = forms.ModelChoiceField(label=_("duration"),
                queryset=conference_models.SessionDuration.current_objects.all())
        if 'track' in self.fields:
            self.fields['track'] = forms.ModelChoiceField(label=_("Track"), required=True, initial=None,
                queryset=tracks)
        if 'description' in self.fields:
            self.fields['description'].help_text = """Bis ca. 50 Worte. Erscheint im gedruckten Programm. <br />Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>."""
            self.fields['description'].validators = [validators.MaxLengthValidator(2000)]
        if 'abstract' in self.fields:
            self.fields['abstract'].help_text = """Darstellung des Vortragsinhalts und ist die Grundlage für das Review.<br />Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>."""
            self.fields['abstract'].validators = [validators.MaxLengthValidator(3000)]
        if 'additional_speakers' in self.fields:
            self.fields['additional_speakers'].help_text = """Aus Sicherheitsgründen müssen Sie in diesem Feld entweder den Vor- oder Nachnamen eines Teilnehmers eintragen, um die Autovervollständigung zu starten."""

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
            Fieldset(_('Details'), ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})), 'tags', 'duration', 'audience_level', Field('additional_speakers', css_class='multiselect-user')),
            ButtonHolder(Submit('submit', button_text, css_class="btn-primary"))
            )

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
            "duration"
        ]

    def __init__(self, *args, **kwargs):
        super(TypedSubmissionForm, self).__init__(*args, **kwargs)
        tracks = conference_models.Track.current_objects.all()
        instance = kwargs.get('instance')
        if instance:
            button_text = u"Änderungen speichern"
        else:
            button_text = u"Vortrag einreichen"
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('title', autofocus="autofocus"),
                Field('description'),
                Field('abstract')),
            Fieldset(_('Details'), ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})), 'tags', 'duration', 'audience_level', Field('additional_speakers', css_class='multiselect-user')),
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
        ]

    def __init__(self, *args, **kwargs):
        super(TutorialSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = "Kurzbeschreibung"
        self.fields['description'].validators.append(validators.MaxWordsValidator(300))
        self.fields['description'].help_text = """Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>.<br />< 300 Worte"""
        self.fields['abstract'].label = "Gliederung"
        self.fields['abstract'].help_text = """Dieses Feld unterstützt <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a>.<br /><br />
                                              Bitte stichpunktartige Angaben zum Aufbau des Tutorials mit Zeitangaben
                                              zu den einzelnen Punkten, wobei die Summe 180 Minuten ergeben muss.
                                              Bitte die benötigen Software-Pakete aufführen, so dass die Teilnehmer
                                              bereits vor dem Tutorial ihre Laptops einrichten können. Bitte Anforderungen
                                              an Versionen angeben und deren Zusammenspiel überprüfen.<br /><br /> Grundsätzlich
                                              sollten die Tutorial-Inhalte auf allen drei gängigen
                                              Betriebssystemen (Linux, Mac OS X und Windows) funktionieren.
                                              Wenn nicht, bitte explizit darauf hinweisen."""

        instance = kwargs.get('instance')
        if instance:
            button_text = u"Änderungen speichern"
        else:
            button_text = u"Tutorial einreichen"
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('title', autofocus="autofocus"),
                Field('description'),
                Field('abstract')),
            Fieldset(_('Details'), 'tags', 'audience_level', Field('additional_speakers', css_class='multiselect-user')),
            ButtonHolder(Submit('submit', button_text, css_class="btn-primary")),
            )

    def customize_save(self, instance):
        instance.duration = conference_models.SessionDuration.current_objects.get(slug='tutorial')


class TalkSubmissionForm(TypedSubmissionForm):
    def __init__(self, *args, **kwargs):
        super(TalkSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['duration'] = forms.ModelChoiceField(label=_("duration"),
                queryset=conference_models.SessionDuration.current_objects.exclude(slug='tutorial').all())
        self.helper.layout.fields.insert(-1, Fieldset('Videoaufzeichnung', HTML(u"""<p class="control-group">Optional können Vorträge auch aufgezeichnet werden. Es liegt während der Konferenz ein Papierformular auf, durch das Sie einer solchen Aufzeichnung zustimmen können. Mehr Informationen dazu finden Sie <a href="/vortragende/">hier</a>.</p>""")))

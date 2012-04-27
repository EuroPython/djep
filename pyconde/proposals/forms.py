from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Fieldset, Submit, Field
from pyconde.forms import ExtendedHelpField

from conference.models import current_conference
from conference import models as conference_models

from . import models


class ProposalSubmissionForm(forms.ModelForm):
    agree_to_terms = forms.BooleanField(label=_("Agree to terms"),
        help_text=_("All sessions have to take place according to a set of rules listed below. In order to submit your session proposal you have to agree to these terms."))

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
        tracks = conference_models.Track.current_objects.all()
        self.fields['kind'] = forms.ModelChoiceField(label=_("kind"),
            queryset=conference_models.SessionKind.current_objects.filter_open_kinds())
        self.fields['audience_level'] = forms.ModelChoiceField(label=_("audience level"),
            queryset=conference_models.AudienceLevel.current_objects.all())
        self.fields['duration'] = forms.ModelChoiceField(label=_("duration"),
            queryset=conference_models.SessionDuration.current_objects.all())
        self.fields['track'] = forms.ModelChoiceField(label=_("Track"), required=True, initial=None,
            queryset=tracks)
        self.fields['description'].help_text = _('This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> syntax.')
        self.fields['abstract'].help_text = _('This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> syntax.')

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(_('General'),
                Field('kind', autofocus="autofocus"),
                'title',
                Field('description'),
                Field('abstract'),
                'agree_to_terms'),
            Fieldset(_('Details'), ExtendedHelpField('track', render_to_string('proposals/tracks-help.html', {'tracks': tracks})), 'tags', 'duration', 'audience_level', 'additional_speakers'),
            ButtonHolder(Submit('submit', _('Submit proposal'), css_class="btn-primary"))
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


class ProposalUpdateForm(object):
    pass

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from pyconde.sponsorship.models import Sponsor, JobOffer


class JobOfferForm(forms.Form):

    sponsor = forms.ModelChoiceField(queryset=[], label=_('Sponsor'))
    reply_to = forms.EmailField(label=_('Reply-To'))
    subject = forms.CharField(label=_('Subject'))
    text = forms.CharField(label=_('Text'), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(JobOfferForm, self).__init__(*args, **kwargs)
        self.fields['sponsor'].queryset = Sponsor.objects.filter(active=True).all()
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'sponsor', 'reply_to', 'subject', 'text',
            ButtonHolder(Submit('submit', _('Send job offer'), css_class='btn btn-primary'))
        )

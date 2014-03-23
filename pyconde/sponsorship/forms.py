from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from pyconde.sponsorship.models import Sponsor, JobOffer


class JobOfferForm(forms.ModelForm):
    class Meta(object):
        model = JobOffer

    def __init__(self, *args, **kwargs):
        super(JobOfferForm, self).__init__(*args, **kwargs)
        self.fields['sponsor'].required = True
        self.fields['sponsor'].queryset = Sponsor.objects.filter(active=True).all()
        self.fields['reply_to'].required = True
        self.fields['subject'].required = True
        self.fields['text'].required = True
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'sponsor', 'reply_to', 'subject', 'text',
            ButtonHolder(Submit('submit', _('Send job offer'), css_class='btn-primary'))
        )

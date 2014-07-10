# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import formsets
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from crispy_forms.bootstrap import FieldWithButtons

from ..accounts.forms import UserModelChoiceField
from ..attendees.models import TicketType
from ..sponsorship.models import Sponsor


def get_ticket_types():
    return TicketType.objects.filter_ondesk()


def get_users():
    return User.objects.select_related('profile') \
                       .only('profile__full_name',
                             'profile__display_name',
                             'profile__user',  # for reverse lookup
                             'username'  # fallback if no display_name
                             ) \
                       .all()


def get_sponsors():
    return Sponsor.objects.filter(active=True).all()


class SearchForm(forms.Form):
    query = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_action = reverse('checkin_search')
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            FieldWithButtons('query', Submit('', _('Search')))
        )


class OnDeskPurchaseForm(forms.Form):

    first_name = forms.CharField(label=_('First name'), max_length=250)
    last_name = forms.CharField(label=_('Last name'), max_length=250)

    company_name = forms.CharField(label=_('Company'), max_length=100, required=False)
    street = forms.CharField(label=_('Street and house number'), max_length=100, required=False)
    zip_code = forms.CharField(label=_('Zip code'), max_length=20, required=False)
    city = forms.CharField(label=_('City'), max_length=100, required=False)
    country = forms.CharField(label=_('Country'), max_length=100, required=False)
    vat_id = forms.CharField(label=_('VAT-ID'), max_length=16, required=False)

    def __init__(self, *args, **kwargs):
        super(OnDeskPurchaseForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        invoice_fields = Fieldset(
            _('Invoice'),
            'first_name',
            'last_name',
            'company_name',
            'street',
            'zip_code',
            'city',
            'country',
            'vat_id',
        )
        self.helper.form_tag = False
        self.helper.layout = Layout(
            invoice_fields,
        )


class EditOnDeskTicketForm(forms.Form):

    first_name = forms.CharField(label=_('First name'), max_length=250)
    last_name = forms.CharField(label=_('Last name'), max_length=250)

    organisation = forms.CharField(label=_('Organization'), max_length=100, required=False)
    user_id = UserModelChoiceField(label=_('User'), queryset=None, required=False)
    sponsor_id = forms.ModelChoiceField(label=_('Sponsor'), queryset=None, required=False)

    def __init__(self, users, sponsors, *args, **kwargs):
        super(EditOnDeskTicketForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].queryset = users
        self.fields['sponsor_id'].queryset = sponsors

        self.helper = FormHelper()
        ticket_fields = Fieldset(
            _('Ticket'),
            'first_name',
            'last_name',
            'organisation',
            'user_id',
            'sponsor_id',
        )
        self.helper.form_tag = False
        self.helper.layout = Layout(
            ticket_fields
        )


class NewOnDeskTicketForm(EditOnDeskTicketForm):

    ticket_type_id = forms.ModelChoiceField(label=_('Ticket type'), queryset=None)

    def __init__(self, ticket_types, *args, **kwargs):
        super(NewOnDeskTicketForm, self).__init__(*args, **kwargs)
        self.fields['ticket_type_id'].queryset = ticket_types

        self.helper.disable_csrf = True
        self.helper.layout[0].fields.insert(0,
            'ticket_type_id')


class BaseOnDeskTicketFormSet(formsets.BaseFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseOnDeskTicketFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False

    def _construct_forms(self):
        self.ticket_types = get_ticket_types()
        self.users = get_users()
        self.sponsors = get_sponsors()
        return super(BaseOnDeskTicketFormSet, self)._construct_forms()

    def _construct_form(self, i, **kwargs):
        kwargs.update({
            'ticket_types': self.ticket_types,
            'users': self.users,
            'sponsors': self.sponsors,
        })
        return super(BaseOnDeskTicketFormSet, self)._construct_form(i, **kwargs)

    @property
    def empty_form(self):
        form = self.form(
            ticket_types=self.ticket_types,
            users=self.users,
            sponsors=self.sponsors,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
        )
        self.add_fields(form, None)
        return form

    @property
    def changed_forms(self):
        for f in self.forms:
            if not f.has_changed():
                continue
            yield f

# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, HTML

from pyconde.conference.models import current_conference
from pyconde.attendees.models import Purchase, Customer, Ticket, Voucher
from pyconde.forms import Submit


PAYMENT_METHOD_CHOICES = (
    ('invoice', _('Invoice')),
    ('creditcard', _('Credit card')),
    ('elv', _('ELV')),
)

terms_of_use_url = (settings.PURCHASE_TERMS_OF_USE_URL
                    if (hasattr(settings, 'PURCHASE_TERMS_OF_USE_URL')
                    and settings.PURCHASE_TERMS_OF_USE_URL) else '#')


class PurchaseForm(forms.ModelForm):
    email = forms.EmailField(label=_('E-Mail'), required=True)

    class Meta:
        model = Purchase
        fields = ('company_name', 'first_name', 'last_name', 'email', 'street',
            'zip_code', 'city', 'country', 'vat_id', 'comments')

    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(_('Billing address'), 'first_name', 'last_name',
                'company_name', 'email', 'street', 'zip_code', 'city',
                'country', 'vat_id', 'comments'),
            ButtonHolder(Submit('submit', _('Continue'), css_class='btn-primary'))
        )

    def save(self, *args, **kwargs):
        customer, created = Customer.objects.get_or_create(
            conference=current_conference(),
            email=self.cleaned_data['email'])

        purchase = super(PurchaseForm, self).save(commit=False)
        purchase.customer = customer

        if (kwargs.get('commit', True)):
            purchase.save()

        return purchase


class TicketQuantityForm(forms.Form):
    quantity = forms.IntegerField(label=_('Quantity'), min_value=0,
        required=False, widget=forms.Select)

    def __init__(self, ticket_type, *args, **kwargs):
        self.ticket_type = ticket_type
        super(TicketQuantityForm, self).__init__(
            prefix='tq-%s' % ticket_type.pk, *args, **kwargs)

        if self.ticket_type.available_tickets < 10:
            max_value = self.ticket_type.available_tickets
        else:
            max_value = 10

        if self.ticket_type.vouchertype_needed:
            max_value = 1

        self.fields['quantity'].max_value = max_value
        self.fields['quantity'].widget.choices = zip(
            range(0, max_value+1), range(0, max_value+1))

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        if value > 0:
            if self.ticket_type.available_tickets < 1:
                raise forms.ValidationError(_('Tickets sold out.'))

            if value > self.ticket_type.available_tickets:
                raise forms.ValidationError(_('Not enough tickets left.'))

            if value > self.fields['quantity'].max_value:
                raise forms.ValidationError(_("You've exceeded the maximum"
                                              " number of items of this type "
                                              "for this purchase"))

        return self.cleaned_data['quantity']


class TicketNameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        assert 'instance' in kwargs, 'instance is required.'

        super(TicketNameForm, self).__init__(
            prefix='tn-%s' % kwargs['instance'].pk, *args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['shirtsize'].queryset = self.fields['shirtsize']\
            .queryset.filter(conference=current_conference())

    class Meta:
        model = Ticket
        fields = ('first_name', 'last_name', 'shirtsize')

    def save(self, *args, **kwargs):
        # Update, save would overwrite other flags too (even if not in `fields`)
        Ticket.objects.filter(pk=self.instance.pk).update(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            shirtsize=self.cleaned_data['shirtsize']
        )


class TicketVoucherForm(forms.ModelForm):
    code = forms.CharField(label=_('Voucher'), max_length=12, required=True)

    def __init__(self, *args, **kwargs):
        assert 'instance' in kwargs, 'instance is required.'

        super(TicketVoucherForm, self).__init__(
            prefix='tv-%s' % kwargs['instance'].pk, *args, **kwargs)

    class Meta:
        model = Ticket
        fields = ('code',)

    def clean_code(self):
        try:
            code = self.cleaned_data['code']
            ticket = Ticket.objects.get(pk=self.instance.pk)
            if not ticket.voucher or ticket.voucher.code != code:
                Voucher.objects.valid().get(
                    code=code,
                    type=ticket.ticket_type.vouchertype_needed)
        except Voucher.DoesNotExist:
            raise forms.ValidationError(_('Voucher verification failed.'))

        return code

    def save(self, *args, **kwargs):
        # Mark voucher as used.
        voucher = Voucher.objects.get(type__conference=current_conference(),
                                      code=self.cleaned_data['code'])
        voucher.is_used = True
        voucher.save()

        # Update, save would overwrite other flags too (even if not in `fields`)
        Ticket.objects.filter(pk=self.instance.pk).update(
            voucher=voucher,
        )


class PurchaseOverviewForm(forms.Form):
    accept_terms = forms.BooleanField(
        label=_("I've read and agree to the terms and conditions."),
        help_text=_('You must accept the <a target="_blank" href="%s">terms and conditions</a>.') % terms_of_use_url,
        error_messages={'required': _('You must accept the terms and conditions.')})
    payment_method = forms.ChoiceField(
        label=_('Payment method'),
        choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect,
        help_text=_('If you choose invoice you will receive an invoice from us.'
                    ' After we receive your money transfer your purchase will'
                    ' be finanized.<br /><br />Credit card payment is handled'
                    ' through <a href="http://www.paymill.com">PayMill</a>.'))

    def __init__(self, *args, **kwargs):
        super(PurchaseOverviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'accept_terms',
            'payment_method',
            ButtonHolder(
                Submit('submit', _('Complete purchase'),
                       css_class='btn-primary'),
                HTML('{% load i18n %}<a class="back" href="{% url \'attendees_purchase_names\' %}">{% trans "Back" %}</a>')
            )
        )
        if hasattr(settings, 'PAYMENT_METHODS') and settings.PAYMENT_METHODS:
            choices = self.fields['payment_method'].choices
            new_choices = []
            for choice in choices:
                if choice[0] in settings.PAYMENT_METHODS:
                    new_choices.append(choice)
            self.fields['payment_method'].choices = new_choices

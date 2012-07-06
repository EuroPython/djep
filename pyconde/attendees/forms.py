# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder

from pyconde.attendees.models import Purchase, Customer, Ticket, Voucher
from pyconde.forms import Submit


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
            Fieldset(_('Invoice address'), 'first_name', 'last_name',
                'company_name', 'email', 'street', 'zip_code', 'city',
                'country', 'vat_id', 'comments'),
            ButtonHolder(Submit('submit', _('Purchase tickets'), css_class='btn-primary'))
        )

    def save(self, *args, **kwargs):
        customer, created = Customer.objects.get_or_create(
            email=self.cleaned_data['email'])

        purchase = super(PurchaseForm, self).save(commit=False)
        purchase.customer = customer
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

        if self.ticket_type.voucher_needed:
            max_value = 1

        self.fields['quantity'].max_value = max_value
        self.fields['quantity'].widget.choices = zip(
            range(0, max_value+1), range(0, max_value+1))

    def clean_quantity(self):
        if self.cleaned_data['quantity'] > 0:
            if self.ticket_type.available_tickets < 1:
                raise forms.ValidationError(_('Ticket sold out.'))

            if self.cleaned_data['quantity'] > self.ticket_type.available_tickets:
                raise forms.ValidationError(_('Not enough tickets left.'))

        return self.cleaned_data['quantity']


class TicketNameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        assert 'instance' in kwargs, 'instance is required.'

        super(TicketNameForm, self).__init__(
            prefix='tn-%s' % kwargs['instance'].pk, *args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = Ticket
        fields = ('first_name', 'last_name')

    def save(self, *args, **kwargs):
        # Update, save would overwrite other flags too (even if not in `fields`)
        Ticket.objects.filter(pk=self.instance.pk).update(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
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
                Voucher.objects.valid().get(code=code)
        except Voucher.DoesNotExist:
            raise forms.ValidationError(_('Voucher verification failed.'))

        return code

    def save(self, *args, **kwargs):
        # Mark voucher as used.
        voucher = Voucher.objects.get(code=self.cleaned_data['code'])
        voucher.is_used = True
        voucher.save()

        # Update, save would overwrite other flags too (even if not in `fields`)
        Ticket.objects.filter(pk=self.instance.pk).update(
            voucher=voucher,
        )

# -*- coding: utf-8 -*-
from django import forms
from django.core.cache import get_cache
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, pgettext
from django.utils.safestring import mark_safe
from django.contrib.auth import models as auth_models

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, HTML

from pyconde.conference.models import current_conference
from pyconde.attendees.models import Purchase, VenueTicket, Voucher,\
    SIMCardTicket, DietaryPreference
from pyconde.forms import Submit

from . import utils
from . import settings


PAYMENT_METHOD_CHOICES = (
    ('invoice', _('Invoice')),
    ('creditcard', _('Credit card')),
    ('elv', _('ELV')),
)

terms_of_use_url = settings.TERMS_OF_USE_URL or '#'


class PurchaseForm(forms.ModelForm):
    email = forms.EmailField(label=_('E-mail'), required=True)

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
            ButtonHolder(Submit('submit', _('Continue'), css_class='btn btn-primary'))
        )

    def save(self, *args, **kwargs):
        purchase = super(PurchaseForm, self).save(commit=False)

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

        self.ticket_limit = self.ticket_type.available_tickets

        if self.ticket_limit is not None and self.ticket_limit < 10:
            max_value = self.ticket_limit
        else:
            max_value = 10

        if self.ticket_type.vouchertype_needed:
            max_value = 1

        self.fields['quantity'].max_value = max_value
        self.fields['quantity'].widget.choices = zip(
            range(0, max_value+1), range(0, max_value+1))

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        available = self.ticket_type.available_tickets
        max_value = self.fields['quantity'].max_value

        if value > 0 and available is not None:
            if self.ticket_type.available_tickets < 1:
                raise forms.ValidationError(_('Tickets sold out.'))

            if value > self.ticket_type.available_tickets:
                raise forms.ValidationError(_('Not enough tickets left.'))

        if max_value is not None and value > max_value:
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
        self.fields['organisation'].required = False
        self.fields['dietary_preferences'] = forms.ModelMultipleChoiceField(
            label=mark_safe(pgettext('nameform', 'Dietary preferences')),
            queryset=DietaryPreference.objects.all(),
            required=False,
            widget=forms.CheckboxSelectMultiple
        )
        if 'dietary_preferences' in kwargs['instance'].related_data:
            self.initial['dietary_preferences'] = [obj.pk for obj in kwargs['instance'].related_data.get('dietary_preferences', [])]
        self.fields['shirtsize'].queryset = self.fields['shirtsize']\
            .queryset.filter(conference=current_conference())
        self.fields['shirtsize'].help_text = _('''Sizing charts: <a href="http://maxnosleeves.spreadshirt.com/shop/info/producttypedetails/Popup/Show/productType/813" target="_blank">Women</a>, <a href="http://maxnosleeves.spreadshirt.com/shop/info/producttypedetails/Popup/Show/productType/812" target="_blank">Men</a>''')

    class Meta:
        model = VenueTicket
        fields = ('first_name', 'last_name', 'organisation', 'shirtsize',
                  'dietary_preferences',)
        exclude = VenueTicket.management_fields

    def save(self, *args, **kwargs):
        # Update, save would overwrite other flags too (even if not in
        # `fields`)
        for fname in self._meta.fields:
            val = self.cleaned_data[fname]
            # Since dietary_preferences is a m2m relation we have to temporarily
            # store it somewhere outside of the usual m2m manager which would
            # automatically persist it.
            if fname == 'dietary_preferences':
                self.instance.related_data[fname] = val
                continue
            setattr(self.instance, fname, val)
        return self.instance


class SIMCardNameForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        assert 'instance' in kwargs, 'instance is required.'

        super(SIMCardNameForm, self).__init__(
            prefix='sc-%s' % kwargs['instance'].pk, *args, **kwargs)

        for fname in self._meta.fields:
            self.fields[fname].required = True
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'yyyy-mm-dd'

    class Meta:
        model = SIMCardTicket
        fields = (
            'gender', 'first_name', 'last_name', 'date_of_birth',
            'hotel_name', 'email', 'street', 'zip_code', 'city',
            'country', 'phone')

    def save(self, *args, **kwargs):
        # Update, save would overwrite other flags too (even if not in
        # `fields`)
        for fname in self._meta.fields:
            val = self.cleaned_data[fname]
            setattr(self.instance, fname, val)
        return self.instance


class TicketVoucherForm(forms.ModelForm):
    code = forms.CharField(label=_('Voucher'), max_length=12, required=True)

    def __init__(self, *args, **kwargs):
        assert 'instance' in kwargs, 'instance is required.'

        super(TicketVoucherForm, self).__init__(
            prefix='tv-%s' % kwargs['instance'].pk, *args, **kwargs)

    class Meta:
        model = VenueTicket
        fields = ('code',)

    def clean_code(self):
        try:
            code = self.cleaned_data['code']
            ticket = self.instance
            voucher = None
            if not ticket.voucher or ticket.voucher.code != code:
                voucher = Voucher.objects.valid().get(
                    code=code,
                    type__conference=current_conference(),
                    type=ticket.ticket_type.vouchertype_needed)
            else:
                voucher = ticket.voucher

            # Make sure that the found voucher is not one of the locked ones.
            cache = get_cache('default')
            if cache.get('voucher_lock:{0}'.format(voucher.pk)) and\
                    not utils.voucher_is_locked_for_session(
                        self.request, voucher):
                raise Voucher.DoesNotExist()
        except Voucher.DoesNotExist:
            raise forms.ValidationError(_('Voucher verification failed.'))

        return code

    def save(self, *args, **kwargs):
        voucher = Voucher.objects.get(type__conference=current_conference(),
                                      code=self.cleaned_data['code'])
        self.instance.voucher = voucher
        utils.lock_voucher(self.request, voucher)


class PurchaseOverviewForm(forms.Form):
    accept_terms = forms.BooleanField(
        label=_("I've read and agree to the terms and conditions."),
        help_text=_('You must accept the <a target="_blank" href="%s">terms and conditions</a>.') % terms_of_use_url,
        error_messages={'required': _('You must accept the terms and conditions.')})
    payment_method = forms.ChoiceField(
        label=_('Payment method'),
        choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.purchase = kwargs.pop('purchase')
        super(PurchaseOverviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'accept_terms',
            'payment_method',
            ButtonHolder(
                Submit('submit', _('Complete purchase'),
                       css_class='btn btn-primary'),
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

        # Filter payment methods if they are not allowed based on the
        # min. amount threshold
        total_amount = self.purchase.payment_total
        new_choices = []
        supported_methods = []
        for choice in self.fields['payment_method'].choices:
            minimum = settings.MIN_TOTAL_FOR_PAYMENT_METHOD.get(choice[0])
            if minimum is None or minimum < total_amount:
                new_choices.append(choice)
                supported_methods.append(choice[0])
        self.fields['payment_method'].choices = new_choices
        self.fields['payment_method'].help_text = self.\
            _get_payment_method_helptext(supported_methods)

        if len(new_choices) == 1:
            self.fields['payment_method'].initial = new_choices[0][0]
            if settings.HIDE_SINGLE_PAYMENT_METHOD:
                self.fields['payment_method'].widget = forms.HiddenInput()

    def _get_payment_method_helptext(self, supported_methods):
        """
        A little helper method that statically builds a helptext for the
        payment methods field depending on what payment methods are presented
        to the user.
        """
        texts = {
            'invoice': ugettext(
                'If you choose invoice you will receive an invoice from us. '
                'After we receive your money transfer your purchase will be '
                'finalized.'),
            'creditcard': ugettext(
                'Credit card payment is handled through '
                '<a href="http://www.paymill.com">PayMill</a>.'
                '<br><br>We accept following credit cards:&nbsp;'
                '<img src="/static_media/assets/images/cc/mastercard-curved-32px.png" alt="MasterCard">&nbsp;'
                '<img src="/static_media/assets/images/cc/visa-curved-32px.png" alt="VISA">')
        }
        result = []
        for method in supported_methods:
            text = texts.get(method)
            if text:
                result.append(text)
        return u'<br><br>'.join(result)


class TicketAssignmentForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        help_text=_("Specify the username/login of the user you want to "
                    "assign this ticket to.")
        )

    def clean_username(self):
        val = self.cleaned_data['username']
        if not auth_models.User.objects.filter(username=val).exists():
            raise ValidationError(_("Couldn't find a user with this username."))
        return val

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super(TicketAssignmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'username',
            ButtonHolder(
                Submit('submit', _('Assign ticket'),
                       css_class='btn btn-primary')
            )
        )


class EditVenueTicketForm(TicketNameForm):
    def __init__(self, *args, **kwargs):
        super(EditVenueTicketForm, self).__init__(*args, **kwargs)
        for field_name in self.instance.ticket_type.get_readonly_fields():
            field = self.fields.get(field_name)
            if not field:
                continue
            field.widget.attrs['readonly'] = 'readonly'
            field.help_text = _('This field is no longer editable.')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'first_name',
            'last_name',
            'organisation',
            'dietary_preferences',
            'shirtsize',
            ButtonHolder(Submit('submit', _('Save changes'), css_class='btn btn-primary'))
        )

    def clean(self):
        cleaned_data = super(EditVenueTicketForm, self).clean()
        for field_name in self.instance.ticket_type.get_readonly_fields():
            field_value = getattr(self.instance, field_name)
            if hasattr(field_value, 'all'):
                field_value = list(field_value.all())
            cleaned_data[field_name] = field_value
        return cleaned_data

    def save(self, *args, **kwargs):
        # The ticketnameform disables the save functionality. Here we need it.
        return super(TicketNameForm, self).save(*args, **kwargs)

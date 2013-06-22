# -*- coding: utf-8 -*-
from datetime import datetime
import decimal
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


PURCHASE_STATES = (
    ('incomplete', _('Purchase incomplete')),
    ('new', _('new')),
    ('invoice_created', _('invoice created')),
    ('payment_received', _('payment received')),
    ('canceled', _('canceled'))
)

PAYMENT_METHOD_CHOICES = (
    ('invoice', _('Invoice')),
    ('creditcard', _('Credit card')),
    ('elv', _('ELV')),
)

PRODUCT_NUMBER_START = getattr(settings, 'ATTENDEES_PRODUCT_NUMBER_START', 1)
CUSTOMER_NUMBER_START = getattr(settings, 'ATTENDEES_CUSTOMER_NUMBER_START', 1)


class VoucherManager(models.Manager):
    def valid(self):
        return self.filter(date_valid__gte=datetime.now, is_used=False)


class Voucher(models.Model):
    code = models.CharField(
        _('Code'), max_length=12, blank=True,
        help_text=_('Can be left blank, code will be created when you save.'))
    remarks = models.CharField(_('Remarks'), max_length=254, blank=True)
    date_valid = models.DateTimeField(
        _('Date (valid)'), blank=False,
        help_text=_('The voucher is valid until this date'))
    is_used = models.BooleanField(_('Is used'), default=False)

    objects = VoucherManager()

    class Meta:
        verbose_name = _('Voucher')
        verbose_name_plural = _('Vouchers')

    def __unicode__(self):
        return '%s %s' % (_('Voucher'), self.code)

    def save(self, *args, **kwargs):
        if len(self.code) < 1:
            self.code = str(uuid.uuid4())[-12:]
        super(Voucher, self).save(*args, **kwargs)


class TicketTypeManager(models.Manager):
    def available(self):
        return self.filter(date_valid_from__lte=datetime.now,
                           date_valid_to__gte=datetime.now, is_active=True)

    def get_next_product_number(self):
        """Returns the next product number."""
        if self.count() > 0:
            last = self.aggregate(models.Max('product_number'))
            return last['product_number__max'] + 1
        else:
            return PRODUCT_NUMBER_START


class TicketType(models.Model):
    product_number = models.IntegerField(
        _('Product number'), blank=True, unique=True,
        help_text=_('Will be created when you save the first time.'))

    name = models.CharField(_('Name'), max_length=50)
    fee = models.FloatField(_('Fee'), default=0)

    max_purchases = models.PositiveIntegerField(
        _('Max purchases'),
        default=0, help_text=_('0 means no limit'))

    is_active = models.BooleanField(_('Is active'), default=False)
    date_valid_from = models.DateTimeField(_('Date (valid from)'), blank=False)
    date_valid_to = models.DateTimeField(_('Date (valid to)'), blank=False)

    voucher_needed = models.BooleanField(_('Voucher needed'), default=False)
    tutorial_ticket = models.BooleanField(_('Tutorial ticket'), default=False)

    remarks = models.TextField(_('Remarks'), blank=True)

    objects = TicketTypeManager()

    class Meta:
        ordering = ('tutorial_ticket', 'product_number', 'voucher_needed',)
        verbose_name = _('Ticket type')
        verbose_name_plural = _('Ticket type')

    def __unicode__(self):
        return '%s (%.2f EUR)' % (self.name, self.fee)

    @property
    def purchases_count(self):
        # Ignore incomplete purchases.
        return self.ticket_set.filter(ticket_type=self).exclude(
            purchase__state='incomplete').count()

    @property
    def available_tickets(self):
        if self.max_purchases < 1:
            return 999
        else:
            available_tickets = self.max_purchases - self.purchases_count
            return available_tickets if available_tickets > 0 else 0

    def save(self, *args, **kwargs):
        if not self.pk:
            self.product_number = TicketType.objects.get_next_product_number()
        super(TicketType, self).save(*args, **kwargs)


class CustomerManager(models.Manager):
    def get_next_customer_number(self):
        if self.count() > 0:
            last = self.aggregate(models.Max('customer_number'))
            return last['customer_number__max'] + 1
        else:
            return CUSTOMER_NUMBER_START


class Customer(models.Model):
    customer_number = models.IntegerField(
        _('Customer number'), blank=True, unique=True,
        help_text=_('Will be created when you save the first time.'))

    email = models.EmailField(_('E-Mail'), max_length=250, blank=False)

    date_added = models.DateTimeField(
        _('Date (added)'), blank=False, default=datetime.now)
    is_exported = models.BooleanField(_('Is exported'), default=False)

    objects = CustomerManager()

    class Meta:
        ordering = ('customer_number', 'email')
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __unicode__(self):
        return '%s (%s)' % (self.email, self.customer_number)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.customer_number = Customer.objects.get_next_customer_number()
        super(Customer, self).save(*args, **kwargs)


class PurchaseManager(models.Manager):
    def get_exportable_purchases(self):
        return self.select_related('customer').filter(
            exported=False,
            state__in=['payment_received', 'new', 'invoice_created'])


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, verbose_name=_('Customer'))
    user = models.ForeignKey(User, null=True, verbose_name=_('User'))

    # Address in purchase because a user maybe wants to different invoices.
    company_name = models.CharField(_('Company'), max_length=100, blank=True)
    first_name = models.CharField(_('First name'), max_length=250, blank=False)
    last_name = models.CharField(_('Last name'), max_length=250, blank=False)

    street = models.CharField(_('Street and house number'), max_length=100)
    zip_code = models.CharField(_('Zip code'), max_length=5)
    city = models.CharField(_('City'), max_length=100)
    country = models.CharField(_('Country'), max_length=100)
    vat_id = models.CharField(_('VAT-ID'), max_length=16, blank=True)

    date_added = models.DateTimeField(
        _('Date (added)'), blank=False, default=datetime.now)
    state = models.CharField(
        _('Status'), max_length=25, choices=PURCHASE_STATES,
        default=PURCHASE_STATES[0][0], blank=False)

    comments = models.TextField(_('Comments'), blank=True)

    payment_method = models.CharField(_('Payment method'), max_length=20,
                                      choices=PAYMENT_METHOD_CHOICES,
                                      default='invoice')
    payment_transaction = models.CharField(_('Transaction ID'), max_length=255,
                                           blank=True)

    exported = models.BooleanField(_('Exported'), default=False)

    objects = PurchaseManager()

    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')

    @property
    def payment_total(self):
        # TODO Maybe it's neccessary to add VAT to payment_total.
        fee_sum = self.ticket_set.aggregate(models.Sum('ticket_type__fee'))
        return fee_sum['ticket_type__fee__sum']

    @property
    def payment_total_in_cents(self):
        return int(decimal.Decimal(self.payment_total) * 100)

    @property
    def payment_fee(self):
        return self.payment_total / 1.19

    @property
    def payment_tax(self):
        return self.payment_total - (self.payment_total / 1.19)

    def __unicode__(self):
        return '%s - %s - %s' % (self.pk, self.customer,
                                 self.get_state_display())


class Ticket(models.Model):
    purchase = models.ForeignKey(Purchase)
    ticket_type = models.ForeignKey(TicketType, verbose_name=_('Ticket type'))

    first_name = models.CharField(_('First name'), max_length=250, blank=True)
    last_name = models.CharField(_('Last name'), max_length=250, blank=True)

    date_added = models.DateTimeField(
        _('Date (added)'), blank=False, default=datetime.now)
    voucher = models.ForeignKey(
        'Voucher', verbose_name=_('Voucher'), blank=True, null=True)

    class Meta:
        ordering = ('ticket_type__tutorial_ticket',
                    'ticket_type__product_number')
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')

    def __unicode__(self):
        return u'%s %s - %s' % (self.first_name, self.last_name,
                                self.ticket_type)

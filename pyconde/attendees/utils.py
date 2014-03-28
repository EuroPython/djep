# -*- coding: utf-8 -*-
import xmlrpclib
import datetime
import decimal
import tablib
import uuid
import logging

from django.core.cache import get_cache
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from redis_cache import get_redis_connection

from . import settings as app_settings
from . import tasks


LOG = logging.getLogger(__name__)


def validate_vatid(own_vatid, other_vatid):
    # TODO: Replace evatr or make it optional using a setting
    try:
        server = xmlrpclib.Server('https://evatr.bff-online.de/')
        data = {}
        for item in xmlrpclib.loads(server.evatrRPC(
                own_vatid.replace(' ', ''),
                other_vatid.replace(' ', ''), '', '', '', '', ''))[0]:
            data[item[0]] = item[1]
        return data['ErrorCode'] == '200'
    except:
        return False


def complete_purchase(request, purchase):
    """
    This method finalizes a purchase, clears voucher locks and sends the
    confirmation email.
    """
    if purchase.payment_method == 'invoice':
        purchase.state = 'new'
    else:
        # Credit card payments are automatically marked as payment received
        # if they enter this stage.
        purchase.state = 'payment_received'

    for ticket in purchase.ticket_set.filter(venueticket__isnull=False).filter(venueticket__voucher__isnull=False).all():
        voucher = ticket.venueticket.voucher
        voucher.is_used = True
        voucher.save()
        unlock_voucher(request, voucher)
    purchase.save()
    purchase.invoice_number = generate_invoice_number()
    purchase.save()
    send_purchase_confirmation_mail(purchase)
    tasks.render_invoice.delay(purchase_id=purchase.id)
    return HttpResponseRedirect(reverse('attendees_purchase_done'))


def send_purchase_confirmation_mail(purchase, recipients=None):
    from . import models
    if recipients is None:
        recipients = [purchase.email]
    send_mail(
        _('Ticket successfully purchased'),
        render_to_string('attendees/mail_purchase_completed.txt', {
            'purchase': purchase,
            'conference': purchase.conference,
            'rounded_vat': round_money_value(purchase.payment_tax),
            'payment_method': dict(models.PAYMENT_METHOD_CHOICES).get(
                purchase.payment_method),
            'terms_of_use_url': app_settings.TERMS_OF_USE_URL
        }),
        settings.DEFAULT_FROM_EMAIL, recipients,
        fail_silently=True
    )


def generate_transaction_description(purchase):
    return settings.PAYMILL_TRANSACTION_DESCRIPTION.format(
        purchase_pk=purchase.pk)


def generate_invoice_filename(purchase):
    from .models import Purchase
    ext = '.json' if app_settings.INVOICE_DISABLE_RENDERING else '.pdf'
    filename = str(uuid.uuid4()) + ext
    while Purchase.objects.filter(invoice_filename=filename).exists():
        filename = str(uuid.uuid4()) + ext
    purchase.invoice_filename = filename
    purchase.save(update_fields=['invoice_filename'])


def round_money_value(val):
    return decimal.Decimal(val).quantize(decimal.Decimal('.01'),
                                         rounding=decimal.ROUND_HALF_UP)


def create_tickets_export(queryset):
    """prepare CSV export of Tickets
    note that we hard-coded exclude all tickets of state incomplete or canceled
    """
    data = tablib.Dataset(headers=['Ticket-ID', 'User-firstname', 'User-lastname',
                                   'Organisation', 'T-Shirt',
                                   'Ticket-Type', 'Ticket-Status',
                                   'Purchase-ID', 'E-Mail (Purchase)' ])
    s = lambda x: x or ''
    for ticket in queryset.select_related('purchase').exclude(
                            purchase__state__in=['incomplete','canceled']):
        data.append((ticket.pk, ticket.first_name, ticket.last_name,
                     s(ticket.purchase.company_name), # orgname of purchaser!
                     s(ticket.shirtsize), ticket.ticket_type,
                     ticket.purchase.state, ticket.purchase.pk,
                     ticket.purchase.email))
    return data


def lock_voucher(request, voucher):
    """
    This marks a voucher as locked with the user's session as well as in the
    global cache to prevent other sessions from using it while keeping it
    available in the current session (if the user restarts the checkout).
    """
    cache = get_cache('default')
    expires = request.session['purchase_state']['expires']
    timeout = expires - datetime.datetime.utcnow()
    cache_key = 'voucher_lock:{0}'.format(voucher.pk)
    cache.set(cache_key, True,
              timeout.total_seconds())
    locked_vouchers = request.session.get('locked_vouchers', [])
    locked_vouchers.append(voucher.pk)
    request.session[cache_key] = expires


def voucher_is_locked_for_session(request, voucher):
    """
    This checks if the a given voucher is marked as locked (available only
    in this session) for the given session.
    """
    cache_key = 'voucher_lock:{0}'.format(voucher.pk)
    expires = request.session.get(cache_key)
    if expires is None:
        return False
    if expires < datetime.datetime.utcnow():
        return False
    return True


def unlock_voucher(request, voucher):
    """
    Unlocks the voucher in the global cache as well as in the current session.
    """
    cache = get_cache('default')
    cache_key = 'voucher_lock:{0}'.format(voucher.pk)
    if cache_key in request.session:
        del request.session[cache_key]
    cache.delete(cache_key)


def generate_invoice_number(sequence_name=None):
    """
    WARNING: This method changes the state in Redis!
    """
    if sequence_name is None:
        sequence_name = app_settings.INVOICE_NUMBER_SEQUENCE_NAME
    conn = get_redis_connection()
    return int(conn.incr(sequence_name))

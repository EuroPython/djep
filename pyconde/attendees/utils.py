# -*- coding: utf-8 -*-
import xmlrpclib
import decimal

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def validate_vatid(own_vatid, other_vatid):
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


def complete_purchase(purchase):
    if purchase.payment_method == 'invoice':
        purchase.state = 'new'
    else:
        # Credit card payments are automatically marked as payment received
        # if they enter this stage.
        purchase.state = 'payment_received'
    purchase.save()
    send_purchase_confirmation_mail(purchase)
    return HttpResponseRedirect(reverse('attendees_purchase_done'))


def send_purchase_confirmation_mail(purchase, recipients=None):
    from . import models
    if recipients is None:
        recipients = [purchase.customer.email, settings.DEFAULT_FROM_EMAIL]

    send_mail(
        _('Ticket successfully purchased'),
        render_to_string('attendees/mail_purchase_completed.html', {
            'purchase': purchase,
            'rounded_vat': round_money_value(purchase.payment_tax),
            'payment_method': dict(models.PAYMENT_METHOD_CHOICES).get(
                purchase.payment_method)
        }),
        settings.DEFAULT_FROM_EMAIL, recipients,
        fail_silently=True
    )


def generate_transaction_description(purchase):
    return settings.PAYMILL_TRANSACTION_DESCRIPTION.format(
        purchase_pk=purchase.pk)


def round_money_value(val):
    return decimal.Decimal(val).quantize(decimal.Decimal('.01'),
                                         rounding=decimal.ROUND_HALF_UP)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _

from invoicegenerator import generate_invoice

from pyconde.celery import app

from . import settings as settings


@app.task(ignore_result=True)
def render_invoice(purchase_id):
    from .exporters import PurchaseExporter
    from .models import Purchase
    from .utils import generate_invoice_filename

    try:
        purchase = Purchase.objects.get_exportable_purchases().get(pk=purchase_id)
    except Purchase.DoesNotExist:
        raise RuntimeError('No exportable purchase found with pk %d' % purchase_id)

    generate_invoice_filename(purchase)
    filepath = purchase.invoice_filepath
    if not os.path.exists(settings.INVOICE_ROOT):
        os.makedirs(settings.INVOICE_ROOT)
    data = PurchaseExporter(purchase).export()

    success, error = False, ''
    iteration = 0
    while not success and iteration < 3:
        try:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            password = bytes(get_random_string(32, chars))
            success, error = generate_invoice.render(
                filepath=filepath,
                data=data,
                basepdf=settings.INVOICE_TEMPLATE_PATH,
                fontdir=settings.INVOICE_FONT_ROOT,
                fontconfig=settings.INVOICE_FONT_CONFIG,
                modify_password=password)
        except Exception as e:
            error = e
        finally:
            iteration += 1

    if not success:
        purchase.invoice_filename = None
        purchase.save(update_fields=['invoice_filename'])
        if isinstance(error, Exception):
            raise error
        else:
            raise RuntimeError('Error exporting purchase pk %d: %s' % (purchase_id, error))
    else:
        purchase.exported = True
        purchase.state = 'invoice_created'
        purchase.save(update_fields=['exported', 'state'])

    # Send invoice to buyer
    send_invoice.delay(purchase_id, (purchase.email_receiver,))
    # Send invoice to orga
    send_invoice.delay(purchase_id, settings.INVOICE_EXPORT_RECIPIENTS)


@app.task(ignore_result=True)
def send_invoice(purchase_id, recipients):
    if not recipients:
        return

    from .models import Purchase

    try:
        purchase = Purchase.objects.get(pk=purchase_id)
    except Purchase.DoesNotExist:
        raise RuntimeError('No purchase found with pk %d' % purchase_id)

    if not purchase.exported:
        # Safe call 'cause exported will be set
        # if send_invoice is invoked again
        render_invoice.delay(purchase_id)
        raise RuntimeError('Invoked rendering of invoice pk %d' % purchase_id)

    subject = _('Your EuroPython 2014 Invoice %(full_invoice_number)s') % {
        'full_invoice_number': purchase.full_invoice_number,
    }
    message = render_to_string('attendees/mail_payment_invoice.html', {
        'first_name': purchase.first_name,
        'last_name': purchase.last_name,
        'conference': purchase.conference,
    })
    msg = EmailMessage(subject, message, to=recipients)
    msg.encoding = 'utf-8'
    filename = '%s.pdf' % purchase.full_invoice_number  # attachment filename
    with open(purchase.invoice_filepath, 'rb') as f:
        content = f.read()
    msg.attach(filename, content)
    msg.send()

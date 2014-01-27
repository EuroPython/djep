# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from email.utils import formataddr

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _

from invoicegenerator import generate_invoice

from pyconde.celery import app


def render(filepath, data):
    from django.core.serializers.json import DjangoJSONEncoder
    with open(filepath, 'w') as f:
        f.write(DjangoJSONEncoder(indent=2).encode(data))
    return True, ''


@app.task
def render_invoice(purchase_id):
    from .exporters import PurchaseExporter
    from .models import Purchase
    from .utils import generate_invoice_filename

    try:
        purchase = Purchase.objects.get_exportable_purchases().get(pk=purchase_id)
    except Purchase.DoesNotExist:
        return None

    generate_invoice_filename(purchase)
    filename = purchase.invoice_filename
    filepath = os.path.join(settings.PURCHASE_INVOICE_ROOT, filename)
    data = PurchaseExporter(purchase).export()

    success, error = False, ''
    iteration = 0
    while not success and iteration < 3:
        try:
            # TODO: Replace with call to pyinvoice
            success, error = generate_invoice.render(filepath=filepath,
                data=data, basepdf=settings.PURCHASE_INVOICE_TEMPLATE_PATH)
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
            raise Exception('Error exporting purchase pk %d: %s' % (purchase_id, error))
    else:
        purchase.exported = True
        purchase.save(update_fields=['exported'])

    name = "%s %s" % (purchase.first_name, purchase.last_name)
    recipient = (formataddr((name, purchase.email)),)  # Need a tuple

    # Send invoice to buyer
    send_invoice.delay(purchase_id, filepath, recipient)
    # Send invoice to orga
    send_invoice.delay(purchase_id, filepath, settings.PURCHASE_EXPORT_RECIPIENTS)


@app.task
def send_invoice(purchase_id, filepath, recipients):
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
    msg = EmailMessage(subject, to=recipients)
    msg.encoding = 'utf-8'
    filename = '%s.pdf' % purchase.full_invoice_number  # attachment filename
    with open(filepath, 'rb') as f:
        content = f.read()
    msg.attach(filename, content)
    msg.send()

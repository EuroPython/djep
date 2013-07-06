import logging
import hashlib

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMessage

from . import models


LOG = logging.getLogger(__name__)


class PurchaseEmailExporter(object):
    """
    This exporter sends an email to a globally specified address for every
    purchase being made in the system. This email contains an attached JSON
    file holding details of that purchase which are then used to generate
    an invoice.
    """

    def __init__(self, recipients=None):
        self.recipients = recipients
        if self.recipients is None:
            self.recipients = settings.PURCHASE_EXPORT_RECIPIENTS

    def __call__(self, purchase):
        from . import utils
        if not self.recipients:
            LOG.warn("No recipients specified. Order won't be exported!")
            return
        json_data = self._purchase_to_json(purchase)
        order_number = utils.get_purchase_number(purchase)
        msg = EmailMessage(
            settings.PURCHASE_EXPORT_SUBJECT.format(
                purchase_number=order_number),
            from_email=settings.DEFAULT_FROM_EMAIL, to=self.recipients,
            headers={
                'X-Data-Checksum': self._create_checksum(json_data)
            })
        msg.encoding = 'utf-8'
        msg.attach('data-{0}.json'.format(order_number), json_data, 'application/json')
        msg.send()
        purchase.exported = True
        purchase.save()

    def _create_checksum(self, data):
        return hashlib.sha1(settings.EXPORT_SECRET_KEY + data).hexdigest()

    def _purchase_to_json(self, purchase):
        from . import utils
        result = {
            'id': utils.get_purchase_number(purchase),
            'pk': purchase.pk,
            'tickets': [],
            'total': purchase.payment_total,
            'currency': 'EUR',
            'status': purchase.state,
            'comments': purchase.comments if purchase.comments else None,
            'date_added': purchase.date_added,
            'payment_address': {
                'email': purchase.customer.email,
                'first_name': purchase.first_name,
                'last_name': purchase.last_name,
                'company': purchase.company_name,
                'address_line': purchase.street,
                'postal_code': purchase.zip_code,
                'country': purchase.country,
                'city': purchase.city,
                'vat_id': purchase.vat_id if purchase.vat_id else None
            },
            'payment_info': {
                'method': purchase.payment_method,
                'transaction_id': purchase.payment_transaction
            }
        }

        for ticket in models.Ticket.objects.select_related(
                'ticket_type', 'voucher').filter(purchase=purchase).all():
            result['tickets'].append({
                'pk': ticket.pk,
                'first_name': ticket.first_name,
                'last_name': ticket.last_name,
                'voucher': None,
                'type': {
                    'product_number': ticket.ticket_type.product_number,
                    'name': ticket.ticket_type.name,
                    'pk': ticket.ticket_type.pk
                },
                'price': ticket.ticket_type.fee
            })

        return DjangoJSONEncoder(indent=2).encode(result)

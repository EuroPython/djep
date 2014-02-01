# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class PurchaseExporter(object):
    """
    This exporter takes an pyconde.attendees.Purchase object and exports it,
    including related tickets and payment information as Python dict. This dict
    is intended to be usable by pyinvoice.
    """

    def __init__(self, purchase):
        self.purchase = purchase

    def export(self):
        return self._export(self.purchase)

    def _export(self, purchase):
        from .models import Ticket
        result = {
            'id': purchase.full_invoice_number,
            'pk': purchase.pk,
            'tickets': [],
            'total': purchase.payment_total,
            'currency': 'EUR',
            'status': purchase.state,
            'comments': purchase.comments,
            'date_added': purchase.date_added.replace(microsecond=0),
            'payment_address': {
                'email': purchase.email,
                'first_name': purchase.first_name,
                'last_name': purchase.last_name,
                'company': purchase.company_name,
                'address_line': purchase.street,
                'postal_code': purchase.zip_code,
                'country': purchase.country,
                'city': purchase.city,
                'vat_id': purchase.vat_id,
            },
            'payment_info': {
                'method': purchase.payment_method,
                'transaction_id': purchase.payment_transaction
            }
        }

        for ticket in Ticket.objects.select_related('ticket_type', 'voucher') \
                                    .filter(purchase=purchase).all():
            result['tickets'].append({
                'pk': ticket.pk,
                'first_name': ticket.first_name,
                'last_name': ticket.last_name,
                'voucher': ticket.voucher and ticket.voucher.code or None,
                'type': {
                    'product_number': ticket.ticket_type.product_number,
                    'name': ticket.ticket_type.name,
                    'pk': ticket.ticket_type.pk
                },
                'price': ticket.ticket_type.fee
            })
        return result

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.urlresolvers import reverse

LOG = logging.getLogger('pyconde.attendees')


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
        from .models import Ticket, VenueTicket
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
            ticket_data = {
                'pk': ticket.pk,
                'title': ticket.invoice_item_title,
                'voucher': None,
                'type': {
                    'product_number': ticket.ticket_type.product_number,
                    'name': ticket.ticket_type.name,
                    'pk': ticket.ticket_type.pk
                },
                'price': ticket.ticket_type.fee
            }
            try:
                if ticket.venueticket.voucher is not None:
                    ticket_data['voucher'] = ticket.venueticket.voucher.code
            except VenueTicket.DoesNotExist:
                pass
            result['tickets'].append(ticket_data)
        return result


class BadgeExporter(object):

    def __init__(self, tickets, base_url=None, indent=settings.DEBUG):
        from django.contrib.sites.models import Site
        self.tickets = tickets
        self.indent = indent
        if base_url is None:
            self.base_url = 'http://%s' % Site.objects.get_current().domain
        else:
            self.base_url = base_url
        self._data = None

    @property
    def json(self):
        import json
        data = self.export()
        return json.dumps(data, indent=self.indent)

    def export(self):
        if getattr(self, '_data', None) is None:
            self._data = self._export(self.tickets)
        return self._data

    def _export(self, tickets):
        from .models import VenueTicket

        result = []
        for ticket in tickets.select_related('purchase', 'user__profile__sponsor__level'):
            if not isinstance(ticket, VenueTicket):
                LOG.warn('Ticket %d is of type %s' % (
                    ticket.pk, ticket.__class__.__name__))
                continue
            purchase = ticket.purchase
            if purchase.state != 'payment_received':
                LOG.warn('%s %d belongs to purchase %s (%d) which has not been paid' % (
                    ticket.__class__.__name__, ticket.pk, purchase.full_invoice_number, purchase.id))
                continue
            user = ticket.user
            profile = None if user is None else user.profile
            badge = {
                'id': ticket.id,
                'uid': user and user.id or None,
                'name': '%s %s' % (ticket.first_name, ticket.last_name),
                'organization': ticket.organisation or purchase.company_name or profile and profile.organisation or None,
                'tags': profile and list(profile.tags.values_list('name', flat=True).all()) or None,
                'profile': user and (self.base_url + reverse('account_profile', kwargs={'uid': user.id})) or None,
                'sponsor': None,
                'days': None,  # Only whole-conference tickets are sold online
                'status': None,
                'tutorials': None,
            }
            if profile and profile.sponsor and profile.sponsor.active:
                sponsor = profile.sponsor
                badge['sponsor'] = {
                    'name': sponsor.name,
                    'level': sponsor.level.name,
                    'website': sponsor.external_url
                }

            # TODO: add data to 'status' field:
            #       'status': ['speaker', 'trainer']

            # TODO: add data to 'tutorials' field:
            #       'tutorials': {
            #           '2014-07-21': [2, 4]
            #           '2014-07-22': [5, 8]
            #       }

            result.append(badge)
        return result
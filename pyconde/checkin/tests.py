# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now

from ..accounts.models import Profile
from ..attendees.models import Purchase, TicketType, VenueTicket


def escape_redirect(s):
    return s.replace('/', '%2F')


class ViewTests(TestCase):

    def setUp(self):
        self.vt_ct = ContentType.objects.get_for_model(VenueTicket)

    def tearDown(self):
        pass

    def _create_user(self, permissions=False):
        user = User.objects.create_user(username='user', password='password')
        if permissions:
            Profile.objects.create(user=user)
            permission = Permission.objects.get(codename='see_checkin_info')
            user.user_permissions.add(permission)
        self.client.login(username='user', password='password')


class SearchViewTests(ViewTests):

    def test_search_required_login(self):
        url = reverse('checkin_search')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_search_no_permission(self):
        self._create_user()

        url = reverse('checkin_search')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_search(self):
        self._create_user(permissions=True)

        url = reverse('checkin_search')
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)


class PurchaseViewTests(ViewTests):

    def setUp(self):
        super(PurchaseViewTests, self).setUp()

        self.purchase = Purchase.objects.create()

    def test_purchase_required_login(self):
        url = reverse('checkin_purchase')

        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_no_permission(self):
        self._create_user()

        url = reverse('checkin_purchase')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase(self):
        self._create_user(permissions=True)

        url = reverse('checkin_purchase')
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_purchase_detail_required_login(self):
        url = reverse('checkin_purchase_detail', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_detail_no_permission(self):
        self._create_user()

        url = reverse('checkin_purchase_detail', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_detail(self):
        self._create_user(permissions=True)

        url = reverse('checkin_purchase_detail', kwargs={'pk': self.purchase.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_purchase_badges_required_login(self):
        url = reverse('checkin_purchase_badges', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_badges_no_permission(self):
        self._create_user()

        url = reverse('checkin_purchase_badges', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_badges(self):
        self._create_user(permissions=True)

        url = reverse('checkin_purchase_badges', kwargs={'pk': self.purchase.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code, 404)  # no tickets

    def test_purchase_invoice_required_login(self):
        url = reverse('checkin_purchase_invoice', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_invoice_no_permission(self):
        self._create_user()

        url = reverse('checkin_purchase_invoice', kwargs={'pk': self.purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_invoice(self):
        self._create_user(permissions=True)

        url = reverse('checkin_purchase_invoice', kwargs={'pk': self.purchase.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_purchase_state_GET(self):
        url = reverse('checkin_purchase_state', kwargs={'pk': self.purchase.pk,
                                                        'new_state': 'foo'})
        self.assertEqual(
            self.client.get(url).status_code,
            405)

    def test_purchase_state_required_login(self):
        url = reverse('checkin_purchase_state', kwargs={'pk': self.purchase.pk,
                                                        'new_state': 'foo'})
        self.assertRedirects(
            self.client.post(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_state_no_permission(self):
        self._create_user()

        url = reverse('checkin_purchase_state', kwargs={'pk': self.purchase.pk,
                                                        'new_state': 'foo'})
        self.assertRedirects(
            self.client.post(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_state(self):
        self._create_user(permissions=True)

        url = reverse('checkin_purchase_state', kwargs={'pk': self.purchase.pk,
                                                        'new_state': 'foo'})
        self.assertEqual(
            self.client.post(url, follow=True).status_code,
            200)

    def test_purchase_state_mark_paid(self):
        self._create_user(permissions=True)

        self.purchase.state = 'invoice_created'
        self.purchase.save(update_fields=['state'])

        url = reverse('checkin_purchase_state', kwargs={'pk': self.purchase.pk,
                                                        'new_state': 'foo'})
        self.assertEqual(self.purchase.state, 'invoice_created')
        self.assertContains(
            self.client.post(url, follow=True),
            'Invalid state.')
        purchase = Purchase.objects.get(id=self.purchase.pk)
        self.assertEqual(purchase.state, 'invoice_created')

        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk,
                                                        'new_state': 'paid'})
        self.assertContains(
            self.client.post(url, follow=True),
            'Purchase marked as paid.')
        purchase = Purchase.objects.get(id=purchase.pk)
        self.assertEqual(purchase.state, 'payment_received')


class TicketViewTests(ViewTests):

    def setUp(self):
        super(TicketViewTests, self).setUp()

        self.purchase = Purchase.objects.create()
        self.ticket_type = TicketType.objects.create(name='ticket_type',
            date_valid_from=now() - datetime.timedelta(days=1),
            date_valid_to=now() + datetime.timedelta(days=1),
            content_type=self.vt_ct)
        self.ticket = VenueTicket.objects.create(purchase=self.purchase,
            ticket_type=self.ticket_type, first_name='John', last_name='Doe')

    def test_ticket_badge_required_login(self):
        url = reverse('checkin_ticket_badge', kwargs={'pk': self.ticket.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_ticket_badge_no_permission(self):
        self._create_user()

        url = reverse('checkin_ticket_badge', kwargs={'pk': self.ticket.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_ticket_badge(self):
        self._create_user(permissions=True)

        url = reverse('checkin_ticket_badge', kwargs={'pk': self.ticket.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_ticket_update_required_login(self):
        url = reverse('checkin_ticket_update', kwargs={'pk': self.ticket.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_ticket_update_no_permission(self):
        self._create_user()

        url = reverse('checkin_ticket_update', kwargs={'pk': self.ticket.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_ticket_update(self):
        self._create_user(permissions=True)

        url = reverse('checkin_ticket_update', kwargs={'pk': self.ticket.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)
        ticket = VenueTicket.objects.get(id=self.ticket.pk)
        self.assertEqual(ticket.first_name, 'John')

        data = {'first_name': 'Jane', 'last_name': 'Smith'}
        self.assertRedirects(
            self.client.post(url, data=data, follow=True),
            reverse('checkin_purchase_detail', kwargs={'pk': self.purchase.pk}))
        ticket = VenueTicket.objects.get(id=ticket.pk)
        self.assertEqual(ticket.first_name, 'Jane')
        self.assertEqual(ticket.last_name, 'Smith')

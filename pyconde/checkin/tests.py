# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..accounts.models import Profile
from ..attendees.models import Purchase


def escape_redirect(s):
    return s.replace('/', '%2F')


class ViewTests(TestCase):

    def test_search_required_login(self):
        url = reverse('checkin_search')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_search_no_permission(self):
        auth_models.User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        url = reverse('checkin_search')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_search(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')
        url = reverse('checkin_search')
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_purchase_required_login(self):
        url = reverse('checkin_purchase')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_no_permission(self):
        auth_models.User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        url = reverse('checkin_purchase')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')
        url = reverse('checkin_purchase')
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_purchase_detail_required_login(self):
        purchase = Purchase.objects.create()
        url = reverse('checkin_purchase_detail', kwargs={'pk': purchase.pk})

        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_detail_no_permission(self):
        auth_models.User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        purchase = Purchase.objects.create()

        url = reverse('checkin_purchase_detail', kwargs={'pk': purchase.pk})
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_detail(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')

        purchase = Purchase.objects.create()
        url = reverse('checkin_purchase_detail', kwargs={'pk': purchase.pk})
        self.assertEqual(
            self.client.get(url, follow=True).status_code,
            200)

    def test_checkin_purchase_state_POST(self):
        purchase = Purchase.objects.create()
        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'foo'})

        self.assertEqual(
            self.client.get(url).status_code,
            405)

    def test_checkin_purchase_state_required_login(self):
        purchase = Purchase.objects.create()
        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'foo'})

        self.assertRedirects(
            self.client.post(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_checkin_purchase_state_no_permission(self):
        auth_models.User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        purchase = Purchase.objects.create()

        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'foo'})
        self.assertRedirects(
            self.client.post(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_checkin_purchase_state(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')

        purchase = Purchase.objects.create()
        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'foo'})
        self.assertEqual(
            self.client.post(url, follow=True).status_code,
            200)

    def test_checkin_purchase_state_mark_paid(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')

        purchase = Purchase.objects.create(state='invoice_created')

        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'foo'})
        self.assertEqual(purchase.state, 'invoice_created')
        self.assertContains(
            self.client.post(url, follow=True),
            'Invalid state.')
        purchase = Purchase.objects.get(id=purchase.pk)
        self.assertEqual(purchase.state, 'invoice_created')

        url = reverse('checkin_purchase_state', kwargs={'pk': purchase.pk, 'new_state': 'paid'})
        self.assertContains(
            self.client.post(url, follow=True),
            'Purchase marked as paid.')
        purchase = Purchase.objects.get(id=purchase.pk)
        self.assertEqual(purchase.state, 'payment_received')

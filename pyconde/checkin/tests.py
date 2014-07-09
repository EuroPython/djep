# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..accounts.models import Profile


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
        self.assertEqual(self.client.get(url, follow=True).status_code, 200)

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
        self.assertEqual(self.client.get(url, follow=True).status_code, 200)

    def test_purchase_done_required_login(self):
        url = reverse('checkin_purchase_done')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_done_no_permission(self):
        auth_models.User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        url = reverse('checkin_purchase_done')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_done(self):
        user = auth_models.User.objects.create_user(username='user', password='password')
        Profile.objects.create(user=user)
        permission = auth_models.Permission.objects.get(codename='see_checkin_info')
        user.user_permissions.add(permission)
        self.client.login(username='user', password='password')
        url = reverse('checkin_purchase_done')
        self.assertEqual(self.client.get(url, follow=True).status_code, 200)

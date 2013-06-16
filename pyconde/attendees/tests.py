from decimal import Decimal

from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import utils


class ViewTests(TestCase):
    def test_purchase_required_login(self):
        url = reverse('attendees_purchase')
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)

    def test_purchase_confirm_required_login(self):
        url = reverse('attendees_purchase_confirm')
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)

    def test_purchase_names_required_login(self):
        url = reverse('attendees_purchase_names')
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)


class PurchaseViewTests(TestCase):

    def setUp(self):
        self.user = auth_models.User.objects.create_user(
            'user', 'user@user.com', 'user')
        self.user.first_name = 'Firstname'
        self.user.last_name = 'Lastname'
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_purchase_form_prefilled(self):
        """The purchase form should be prefilled with the current user's
        firstname, lastname and e-mail address."""
        self.client.login(username='user', password='user')
        resp = self.client.get(reverse('attendees_purchase'))
        initial = resp.context['form'].initial
        self.assertEqual('Firstname', initial['first_name'])
        self.assertEqual('Lastname', initial['last_name'])
        self.assertEqual('user@user.com', initial['email'])


class UtilsTests(TestCase):
    def test_rounding(self):
        self.assertEqual(Decimal('1.25'),
                         utils.round_money_value(Decimal('1.245')))
        self.assertEqual(Decimal('1.24'),
                         utils.round_money_value(Decimal('1.244')))
        self.assertEqual(Decimal('1.25'),
                         utils.round_money_value(1.245))

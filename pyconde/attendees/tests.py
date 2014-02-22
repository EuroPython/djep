import datetime
from decimal import Decimal

from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import utils
from . import forms
from . import models


def escape_redirect(s):
    return s.replace('/', '%2F')


class ViewTests(TestCase):
    def test_purchase_required_login(self):
        url = reverse('attendees_purchase')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_confirm_required_login(self):
        url = reverse('attendees_purchase_confirm')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))

    def test_purchase_names_required_login(self):
        url = reverse('attendees_purchase_names')
        self.assertRedirects(
            self.client.get(url, follow=True),
            '/en/accounts/login/?next=' + escape_redirect(url))


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


class TicketQuantityFormTests(TestCase):
    def setUp(self):
        now = datetime.datetime.now()
        self.voucher_type = models.VoucherType()
        self.voucher_type.save()
        self.ticket_type_with_voucher = models.TicketType(
            is_active=True,
            date_valid_from=now,
            date_valid_to=now + datetime.timedelta(days=365),
            vouchertype_needed=self.voucher_type)
        self.ticket_type_with_voucher.save()

    def tearDown(self):
        self.voucher_type.delete()
        self.ticket_type_with_voucher.delete()

    def test_max_amount_with_voucher(self):
        """
        A ticket that requires a voucher can only have the qty of 1.
        """
        form = forms.TicketQuantityForm(
            self.ticket_type_with_voucher, data={'tq-{0}-quantity'.format(self.ticket_type_with_voucher.pk): 2})
        self.assertFalse(form.is_valid())


class TicketVoucherFormTests(TestCase):
    def setUp(self):
        now = datetime.datetime.now()
        self.user = auth_models.User.objects.create_user('test_user', 'test@test.com', 'test_password')
        self.voucher_type = models.VoucherType(name='type1')
        self.voucher_type.save()
        self.voucher_type2 = models.VoucherType(name='type2')
        self.voucher_type2.save()
        self.voucher = models.Voucher(
            type=self.voucher_type,
            date_valid=now + datetime.timedelta(days=1))
        self.voucher.save()
        self.voucher2 = models.Voucher(
            type=self.voucher_type2,
            date_valid=now + datetime.timedelta(days=1))
        self.voucher2.save()
        self.voucher = models.Voucher.objects.get(pk=self.voucher.pk)
        self.voucher2 = models.Voucher.objects.get(pk=self.voucher2.pk)
        self.purchase = models.Purchase(
            user=self.user, first_name='First name', last_name='Last name',
            street='street 123', zip_code='1234', city='city',
            country='country', email='test@test.com')
        self.purchase.save()
        self.ticket_type = models.TicketType(
            name='test',
            date_valid_from=now,
            date_valid_to=now + datetime.timedelta(days=1),
            vouchertype_needed=self.voucher_type)
        self.ticket_type.save()
        self.ticket = models.Ticket(purchase=self.purchase,
                                    ticket_type=self.ticket_type)
        self.ticket.save()

    def tearDown(self):
        self.ticket_type.delete()
        self.user.delete()

    def test_code_validation(self):
        form = forms.TicketVoucherForm(instance=self.ticket, data={
            'tv-{0}-code'.format(self.ticket.pk): 123
        })
        self.assertFalse(form.is_valid())
        form = forms.TicketVoucherForm(instance=self.ticket, data={
            'tv-{0}-code'.format(self.ticket.pk): self.voucher.code
        })
        self.assertTrue(form.is_valid())
        form = forms.TicketVoucherForm(instance=self.ticket, data={
            'tv-{0}-code'.format(self.ticket.pk): self.voucher2.code
        })
        self.assertFalse(form.is_valid())

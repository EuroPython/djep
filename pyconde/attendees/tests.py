import datetime
import mock

from decimal import Decimal
from os import path, unlink

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.test import TestCase

from . import utils
from . import forms
from . import models
from ..conference.models import Conference


def escape_redirect(s):
    return s.replace('/', '%2F')


def ctype(model):
    return ContentType.objects.get_for_model(model)


# used to mock the redis connection
def get_next_invoice_number():
    def wrapper(sequence_name=None):
        last = models.Purchase.objects.aggregate(last=Max('invoice_number'))['last']
        if last is None:
            return 1
        else:
            return last + 1
    return wrapper


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
            name='with voucher',
            is_active=True,
            date_valid_from=now,
            date_valid_to=now + datetime.timedelta(days=365),
            vouchertype_needed=self.voucher_type,
            content_type=ctype(models.VenueTicket)
            )
        self.ticket_type_without_limit = models.TicketType(
            name='without limit',
            is_active=True,
            date_valid_from=now,
            date_valid_to=now + datetime.timedelta(days=365),
            max_purchases=0,
            content_type=ctype(models.VenueTicket)
            )
        self.ticket_type_with_limit = models.TicketType(
            name='with limit',
            is_active=True,
            date_valid_from=now,
            date_valid_to=now + datetime.timedelta(days=365),
            max_purchases=2,
            content_type=ctype(models.VenueTicket)
            )
        self.ticket_type_without_limit.save()
        self.ticket_type_with_limit.save()
        self.ticket_type_with_voucher.save()

    def tearDown(self):
        self.voucher_type.delete()
        self.ticket_type_without_limit.delete()
        self.ticket_type_with_limit.delete()
        self.ticket_type_with_voucher.delete()

    def test_max_amount_with_voucher(self):
        """
        A ticket that requires a voucher can only have the qty of 1.
        """
        qty_key = 'tq-{0}-quantity'.format(self.ticket_type_with_voucher.pk)
        form = forms.TicketQuantityForm(
            self.ticket_type_with_voucher,
            data={qty_key: 2})
        self.assertFalse(form.is_valid())

    def test_max_amount_without_limit(self):
        """
        A ticket that has a limit set should have this value be enforced.
        """
        qty_key = 'tq-{0}-quantity'.format(self.ticket_type_without_limit.pk)
        form = forms.TicketQuantityForm(
            self.ticket_type_without_limit,
            data={qty_key: 2})
        self.assertTrue(form.is_valid())

    def test_max_amount_exceeded_with_limit(self):
        """
        A ticket that has a limit set should have this value be enforced.
        """
        form = forms.TicketQuantityForm(
            self.ticket_type_with_limit,
            data={'tq-{0}-quantity'.format(self.ticket_type_with_limit.pk): 3})
        self.assertFalse(form.is_valid())

    def test_max_amount_valid_with_limit(self):
        """
        If the request amount doesn't exceed the maximum amount then the
        form is valid.
        """
        form = forms.TicketQuantityForm(
            self.ticket_type_with_limit,
            data={'tq-{0}-quantity'.format(self.ticket_type_with_limit.pk): 2})
        self.assertTrue(form.is_valid())


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
            vouchertype_needed=self.voucher_type,
            content_type=ctype(models.VenueTicket))
        self.ticket_type.save()
        self.ticket = models.VenueTicket(purchase=self.purchase,
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


class TicketAssignmentFormTests(TestCase):
    def setUp(self):
        self.user1 = auth_models.User.objects.create_user(
            'test_user1', 'test1@test.com', 'test_password')
        self.user2 = auth_models.User.objects.create_user(
            'test_user2', 'test2@test.com', 'test_password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_username_required(self):
        form = forms.TicketAssignmentForm()
        self.assertFalse(form.is_valid())

    def test_non_existing_username(self):
        form = forms.TicketAssignmentForm(
            current_user=self.user1,
            data={'username': 'i-dont-exist@test.com'})
        self.assertFalse(form.is_valid())

    def test_username_not_of_current_user(self):
        form = forms.TicketAssignmentForm(
            current_user=self.user1,
            data={'username': self.user2.username})
        self.assertTrue(form.is_valid())

    def test_username_of_current_user(self):
        form = forms.TicketAssignmentForm(
            current_user=self.user1,
            data={'username': self.user1.username})
        self.assertFalse(form.is_valid())


class PurchaseOverviewFormTests(TestCase):
    def test_creditcard_unavailable_for_zero_total(self):
        form = forms.PurchaseOverviewForm(
            purchase=models.Purchase(payment_total=0.0))
        available_methods = [c[0] for c in form.fields['payment_method'].choices]
        self.assertNotIn('creditcard', available_methods)

    def test_creditcard_available_for_gtzero_total(self):
        form = forms.PurchaseOverviewForm(
            purchase=models.Purchase(payment_total=0.01))
        available_methods = [c[0] for c in form.fields['payment_method'].choices]
        self.assertIn('creditcard', available_methods)


class PurchaseProcessTest(TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.purchase_start = self.now - datetime.timedelta(days=5)
        self.purchase_end = self.now + datetime.timedelta(days=25)

        self.ct_venueticket = ctype(models.VenueTicket)
        self.ct_simcardticket = ctype(models.SIMCardTicket)
        self.ct_supportticket = ctype(models.SupportTicket)

        self.user = auth_models.User.objects.create_user(username='user',
            email='user@user.com', password='user')
        self.client.login(username='user', password='user')

        # setup the conference
        self.conference = Conference.objects.create(title='TestConf')

        # setup the voucher types and vouchers
        self.vt_student = models.VoucherType.objects.create(
            conference=self.conference, name='VT:Student')
        self.vt_fin_aid = models.VoucherType.objects.create(
            conference=self.conference, name='VT:FinAid')
        self.v_student = models.Voucher.objects.create(
            remarks='V:Student', date_valid=self.purchase_end,
            type=self.vt_student)
        self.v_fin_aid = models.Voucher.objects.create(
            remarks='V:FinAid', date_valid=self.purchase_end,
            type=self.vt_fin_aid)

        # setup the ticket types
        self.tt_conf_student = models.TicketType.objects.create(
            conference=self.conference, name='TT:Student', fee=100,
            is_active=True, date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            vouchertype_needed=self.vt_student,
            content_type=self.ct_venueticket)
        self.tt_conf_standard = models.TicketType.objects.create(
            conference=self.conference, name='TT:Standard', fee=200,
            max_purchases=7, is_active=True,
            date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            content_type=self.ct_venueticket)
        self.tt_conf_finaid = models.TicketType.objects.create(
            conference=self.conference, name='TT:FinAid', fee=0,
            is_active=True, date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            vouchertype_needed=self.vt_fin_aid,
            content_type=self.ct_venueticket)
        self.tt_sim = models.TicketType.objects.create(
            conference=self.conference, name='TT:SIM', fee=12.34,
            is_active=True, date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            content_type=self.ct_simcardticket)
        self.tt_support10 = models.TicketType.objects.create(
            conference=self.conference, name='TT:Support10', fee=10,
            is_active=True, date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            content_type=self.ct_supportticket)
        self.tt_support50 = models.TicketType.objects.create(
            conference=self.conference, name='TT:Support50', fee=50,
            is_active=True, date_valid_from=self.purchase_start,
            date_valid_to=self.purchase_end,
            content_type=self.ct_supportticket)

        # setup the t-shirts sizes
        self.ts_mxl = models.TShirtSize.objects.create(
            conference=self.conference, size='TS:MaleXL', sort=2)
        self.ts_fm = models.TShirtSize.objects.create(
            conference=self.conference, size='TS:FemaleM', sort=1)

    def tearDown(self):
        for purchase in models.Purchase.objects.all():
            if path.exists(purchase.invoice_filepath):
                unlink(purchase.invoice_filepath)

        for klass in [models.Purchase, models.VenueTicket, models.SIMCardTicket,
                      models.SupportTicket, models.Ticket, models.TShirtSize,
                      models.TicketType, models.Voucher, models.VoucherType,
                      Conference]:
            for inst in klass.objects.all():
                inst.delete()

    def assertQuantityForm(self, response, ticket_type, limit):
        text = '<select id="id_tq-%d-quantity" name="tq-%d-quantity">' % (
            ticket_type.pk, ticket_type.pk)
        for i in range(0, limit + 1):
            text += '<option value="%d">%d</option>' % (i, i)
        text += '</select>'
        self.assertContains(response, text, html=True)

    def assertNameForm(self, response, ticket, ticket_klass):
        t_pk = ticket.pk
        self.assertIsInstance(ticket, ticket_klass)
        if isinstance(ticket, models.VenueTicket):
            self.assertContains(response,
                '<input id="id_tn-%d-first_name" maxlength="250" name="tn-%d-first_name" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_tn-%d-last_name" maxlength="250" name="tn-%d-last_name" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_tn-%d-organisation" maxlength="100" name="tn-%d-organisation" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<select id="id_tn-%d-shirtsize" name="tn-%d-shirtsize">'
                '<option value="" selected="selected">---------</option>'
                '<option value="%d">TS:FemaleM</option>'
                '<option value="%d">TS:MaleXL</option>'
                '</select>' % (t_pk, t_pk, self.ts_fm.pk, self.ts_mxl.pk),
                count=1, html=True)
        elif isinstance(ticket, models.SIMCardTicket):
            self.assertContains(response,
                '<select id="id_sc-%d-gender" name="sc-%d-gender">'
                '<option value="" selected="selected">---------</option>'
                '<option value="female">female</option>'
                '<option value="male">male</option>'
                '</select>' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-first_name" maxlength="250" name="sc-%d-first_name" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-last_name" maxlength="250" name="sc-%d-last_name" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-date_of_birth" name="sc-%d-date_of_birth" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-hotel_name" maxlength="100" name="sc-%d-hotel_name" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-email" maxlength="75" name="sc-%d-email" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-street" maxlength="100" name="sc-%d-street" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-zip_code" maxlength="20" name="sc-%d-zip_code" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-city" maxlength="100" name="sc-%d-city" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-country" maxlength="100" name="sc-%d-country" type="text" />' % (t_pk, t_pk),
                count=1, html=True)
            self.assertContains(response,
                '<input id="id_sc-%d-phone" maxlength="100" name="sc-%d-phone" type="text" />' % (t_pk, t_pk),
                count=1, html=True)

    def assertVoucherForm(self, response, ticket):
        t_pk = ticket.pk
        self.assertContains(response,
            '<input id="id_tv-%d-code" maxlength="12" name="tv-%d-code" type="text" />' % (t_pk, t_pk),
            count=1, html=True)

    def assertTicketInOverview(self, response, ticket_type, first_name, last_name, amount, count=1):
        text = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            ticket_type, first_name, last_name, amount)
        self.assertContains(response, text, count=count, html=True)

    @mock.patch('pyconde.attendees.utils.generate_invoice_number',
                new_callable=get_next_invoice_number)
    def test_valid_purchase_process(self, mock_gen_inv_nr):
        response = self.client.get(reverse('attendees_purchase'))

        # check we are on the start page
        self.assertContains(response, '<li class="active">Start</li>', html=True)

        # check for ticket type names:
        self.assertContains(response, 'TT:Student (100.00 EUR)')
        self.assertContains(response, 'TT:Standard (200.00 EUR)')
        self.assertContains(response, 'TT:FinAid (0.00 EUR)')
        self.assertContains(response, 'TT:SIM (12.34 EUR)')
        self.assertContains(response, 'TT:Support10 (10.00 EUR)')
        self.assertContains(response, 'TT:Support50 (50.00 EUR)')

        self.assertQuantityForm(response, self.tt_conf_student, 1)
        self.assertQuantityForm(response, self.tt_conf_standard, 7)
        self.assertQuantityForm(response, self.tt_conf_finaid, 1)
        self.assertQuantityForm(response, self.tt_sim, 10)
        self.assertQuantityForm(response, self.tt_support10, 10)
        self.assertQuantityForm(response, self.tt_support50, 10)

        # TODO: Check for purchase form (billing address, etc.)

        # Post the quantity and purchase data
        data = {
            # quantities
            'tq-%d-quantity' % self.tt_conf_student.pk: 1,
            'tq-%d-quantity' % self.tt_conf_standard.pk: 2,
            'tq-%d-quantity' % self.tt_conf_finaid.pk: 1,
            'tq-%d-quantity' % self.tt_sim.pk: 2,
            'tq-%d-quantity' % self.tt_support10.pk: 0,
            'tq-%d-quantity' % self.tt_support50.pk: 4,

            # billing address
            'city': 'P:Berlin',
            'comments': 'P:SomeComment',
            'company_name': 'P:ExCom',
            'country': 'P:Germany',
            'email': 'purchase@example.com',
            'first_name': 'P:FirstName',
            'last_name': 'P:LastName',
            'street': 'P:Street 123',
            'vat_id': 'P:V4TID',
            'zip_code': 'P:Z1P-2345',
        }
        response = self.client.post(reverse('attendees_purchase'), data=data)
        self.assertRedirects(response, reverse('attendees_purchase_names'))

        # check for created tickets
        tickets = self.client.session['purchase_state']['tickets']
        self.assertIsInstance(tickets[0], models.VenueTicket)
        self.assertIsInstance(tickets[1], models.VenueTicket)
        self.assertIsInstance(tickets[2], models.VenueTicket)
        self.assertIsInstance(tickets[3], models.VenueTicket)

        self.assertIsInstance(tickets[4], models.SIMCardTicket)
        self.assertIsInstance(tickets[5], models.SIMCardTicket)

        self.assertIsInstance(tickets[6], models.SupportTicket)
        self.assertIsInstance(tickets[7], models.SupportTicket)
        self.assertIsInstance(tickets[8], models.SupportTicket)
        self.assertIsInstance(tickets[9], models.SupportTicket)
        for i in range(10):
            self.assertEqual(tickets[i].pk, i)  # Check for temp pk

        # TODO: check for created purchase object

        response = self.client.get(reverse('attendees_purchase_names'))

        # check we are on the names page
        self.assertContains(response, '<li class="active">Ticket info</li>', html=True)

        # check for name forms labels
        self.assertContains(response, '<legend>1. Ticket (TT:Student)</legend>', count=1, html=True)
        self.assertContains(response, '<legend>2. Ticket (TT:Standard)</legend>', count=1, html=True)
        self.assertContains(response, '<legend>3. Ticket (TT:Standard)</legend>', count=1, html=True)
        self.assertContains(response, '<legend>4. Ticket (TT:FinAid)</legend>', count=1, html=True)
        self.assertContains(response, '<legend>Voucher</legend>', count=1, html=True)
        self.assertContains(response,
            '<label for="" class="requiredField"> 1. TT:Student <span class="asteriskField">*</span></label>',
            count=1, html=True)
        self.assertContains(response,
            '<label for="" class="requiredField"> 2. TT:FinAid <span class="asteriskField">*</span></label>',
            count=1, html=True)
        self.assertContains(response, '<legend>SIM Card(s)</legend>', count=1, html=True)
        self.assertContains(response, '<legend>1. TT:SIM</legend>', count=1, html=True)
        self.assertContains(response, '<legend>2. TT:SIM</legend>', count=1, html=True)

        # check for form fields
        tickets = self.client.session['purchase_state']['tickets']
        for i in range(4):
            self.assertNameForm(response, tickets[i], models.VenueTicket)
        for i in range(4, 6):
            self.assertNameForm(response, tickets[i], models.SIMCardTicket)

        self.assertVoucherForm(response, tickets[0])  # Student
        self.assertVoucherForm(response, tickets[3])  # FinAid

        # Post the ticket names
        data = {}
        shirtsizes = (self.ts_fm.pk, self.ts_mxl.pk)
        for i in range(4):
            data.update({
                'tn-%d-first_name' % tickets[i].pk: 'TN:%d:FirstName' % i,
                'tn-%d-last_name' % tickets[i].pk: 'TN:%d:LastName' % i,
                'tn-%d-organisation' % tickets[i].pk: 'TN:%d:Organisation' % i,
                'tn-%d-shirtsize' % tickets[i].pk: shirtsizes[i % 2],
            })
        for i in range(4, 6):
            data.update({
                'sc-%d-gender' % tickets[i].pk: (i % 2) and 'male' or 'female',
                'sc-%d-first_name' % tickets[i].pk: 'SC:%d:FirstName' % i,
                'sc-%d-last_name' % tickets[i].pk: 'SC:%d:LastName' % i,
                'sc-%d-date_of_birth' % tickets[i].pk: '2014-0%d-0%d' % (i, i),
                'sc-%d-hotel_name' % tickets[i].pk: 'SC:%d:HotelName' % i,
                'sc-%d-email' % tickets[i].pk: 'sc-%d@example.com' % i,
                'sc-%d-street' % tickets[i].pk: 'SC:%d:Street %d' % (i, i),
                'sc-%d-zip_code' % tickets[i].pk: 'SC:%d:ZIP' % i,
                'sc-%d-city' % tickets[i].pk: 'SC:%d:City' % i,
                'sc-%d-country' % tickets[i].pk: 'SC:%d:Country' % i,
                'sc-%d-phone' % tickets[i].pk: 'SC:%d:Phone' % i,
            })
        data.update({
            'tv-0-code': self.v_student.code,
            'tv-3-code': self.v_fin_aid.code,
        })

        response = self.client.post(reverse('attendees_purchase_names'), data=data)
        self.assertRedirects(response, reverse('attendees_purchase_confirm'))

        # TODO: check ticket data

        response = self.client.get(reverse('attendees_purchase_confirm'))

        # check we are on the confirmation page
        self.assertContains(response, '<li class="active">Overview</li>', html=True)

        # check for ticket list
        self.assertTicketInOverview(response, 'TT:Student', 'TN:0:FirstName',
            'TN:0:LastName', '100.00 EUR')
        self.assertTicketInOverview(response, 'TT:Standard', 'TN:1:FirstName',
            'TN:1:LastName', '200.00 EUR')
        self.assertTicketInOverview(response, 'TT:Standard', 'TN:2:FirstName',
            'TN:2:LastName', '200.00 EUR')
        self.assertTicketInOverview(response, 'TT:FinAid', 'TN:3:FirstName',
            'TN:3:LastName', '0.00 EUR')
        self.assertTicketInOverview(response, 'TT:SIM', 'SC:4:FirstName',
            'SC:4:LastName', '12.34 EUR')
        self.assertTicketInOverview(response, 'TT:SIM', 'SC:5:FirstName',
            'SC:5:LastName', '12.34 EUR')
        self.assertTicketInOverview(response, 'TT:Support50', '', '',
            '50.00 EUR', count=4)

        # check for billing address and total
        self.assertContains(response,
            '<p>'
            'P:ExCom<br />'
            'P:FirstName P:LastName<br />'
            'P:Street 123<br />'
            'P:Z1P-2345 P:Berlin<br />'
            'P:Germany<br />'
            '</p>', count=1, html=True)
        self.assertContains(response, '<td>724.68 EUR</td>', count=1, html=True)

        data = {
            'accept_terms': True,
            'payment_method': 'invoice',
        }

        response = self.client.post(reverse('attendees_purchase_confirm'), data=data, follow=True)
        # TODO: check persisted ticket data

        # check we are on the completion page
        self.assertContains(response, '<li class="active">Complete</li>', html=True)


class TestTicketTypes(TestCase):
    def setUp(self):
        now = datetime.datetime.now()
        self.venue_ticket_type = models.TicketType(name="test", fee=100,
               date_valid_from=now - datetime.timedelta(days=-1),
               date_valid_to=now + datetime.timedelta(days=1),
               editable_fields='shirtsize')
        self.venue_ticket_type.content_type = ContentType.objects.get(
            app_label='attendees', model='venueticket')
        self.venue_ticket_type.save()

    def tearDown(self):
        self.venue_ticket_type.delete()

    def test_returns_all_tickettypes(self):
        """
        All subclasses of attendees.ticket should provided by
        limit_ticket_types including ticket itself.
        """
        from django.db.models import get_models
        expected = set()
        found = set()
        for model in get_models():
            if issubclass(model, models.Ticket):
                expected.add("{0}.{1}".format(
                    model._meta.app_label,
                    model.__name__.lower()))
        for node in models.limit_ticket_types().children:
            values = dict(node.children)
            found.add("{0}.{1}".format(
                values['app_label'], values['model']))
        self.assertEqual(expected, found)

    def test_get_editable_fields_empty(self):
        """
        If the field is empty, an empty list should be returned.
        """
        self.assertEqual([], models.TicketType(editable_fields="").get_editable_fields())

    def test_get_editable_fields_default(self):
        """
        By default no fields should be marked as editable.
        """
        self.assertEqual([], models.TicketType().get_editable_fields())

    def test_get_editable_fields_spaces(self):
        """
        The list of editable fields should be specified as a comma-separated string
        with arbitrary spaces.
        """
        expected = ["a", "b", "c"]
        inputs = [
            "a, b, c",
            "   a,b    ,c",
            "a,b,c,"
        ]

        for input in inputs:
            self.assertEquals(expected, models.TicketType(editable_fields=input).get_editable_fields())

    def test_get_readonly_fields(self):
        fields = set(self.venue_ticket_type.get_readonly_fields())
        expected = set(['first_name', 'last_name', 'organisation', 'voucher'])
        self.assertEqual(expected, fields)


class TestTicketModel(TestCase):
    def test_ticket_editable_if_enabled_on_tickettype(self):
        user = auth_models.User()
        conference = Conference(tickets_editable=True)
        ticket_type = models.TicketType(allow_editing=True,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertTrue(ticket.can_be_edited_by(user))

    def test_ticket_editable_if_enabled_on_conference(self):
        user = auth_models.User()
        conference = Conference(tickets_editable=True)
        ticket_type = models.TicketType(allow_editing=None,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertTrue(ticket.can_be_edited_by(user))

    def test_ticket_editable_if_enabled_on_ticket_and_disabled_on_conference(self):
        user = auth_models.User()
        conference = Conference(tickets_editable=False)
        ticket_type = models.TicketType(allow_editing=True,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertTrue(ticket.can_be_edited_by(user))

    def test_ticket_not_editable_if_disabled_on_ticket(self):
        user = auth_models.User()
        conference = Conference(tickets_editable=True)
        ticket_type = models.TicketType(allow_editing=False,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertFalse(ticket.can_be_edited_by(user))

    def test_ticket_not_editable_if_disabled_on_conference(self):
        user = auth_models.User()
        conference = Conference(tickets_editable=False)
        ticket_type = models.TicketType(allow_editing=None,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertFalse(ticket.can_be_edited_by(user))

    def test_ticket_not_editable_if_time_over_on_tickettype(self):
        user = auth_models.User()
        now = datetime.datetime.now()
        conference = Conference(tickets_editable=True)
        ticket_type = models.TicketType(allow_editing=True,
                                        editable_until=now + datetime.timedelta(days=-1),
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertFalse(ticket.can_be_edited_by(user, current_time=now))

    def test_ticket_not_editable_if_time_over_on_conference(self):
        user = auth_models.User()
        now = datetime.datetime.now()
        conference = Conference(tickets_editable=True,
                                tickets_editable_until=now + datetime.timedelta(days=-1))
        ticket_type = models.TicketType(allow_editing=True,
                                        conference=conference)
        ticket = models.Ticket(ticket_type=ticket_type, user=user)
        self.assertFalse(ticket.can_be_edited_by(user, current_time=now))


class TestVenueTicketModel(TestCase):
    def test_get_fields(self):
        expected = set(['first_name', 'last_name', 'organisation', 'shirtsize', 'voucher'])
        fields = models.VenueTicket.get_fields()
        self.assertEqual(expected, fields)


class TestSupportTicketModel(TestCase):
    def test_get_fields(self):
        expected = set()
        fields = models.SupportTicket.get_fields()
        self.assertEqual(expected, fields)

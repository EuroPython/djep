# -*- coding: utf-8 -*-
"""
The purchase process consists of the following steps:

1. Enter address data and select what tickets you want to purchase.
2. Enter the names the tickets should be assigned to.
3. Offer an overview and means to choose a payment method
4. Handle payment (optional depending on the chosen payment method)
5. Finalize the purchase, show a confirmation page and send the respective
   emails.

"""
import datetime
import decimal
import logging
from collections import OrderedDict

import pymill

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
import django.views.generic as generic_views

from braces.views import LoginRequiredMixin

from .models import TicketType, Ticket, Purchase
from . import forms
from . import utils


LOG = logging.getLogger(__name__)


class PurchaseMixin(object):
    """
    This is a general mixin that ensures that the right purchase is available
    and that the user doesn't jump ahead from view to view when not all
    the required steps have been visited.
    """
    purchase = None
    steps = OrderedDict([
        ('start', 'attendees_purchase'),
        ('names', 'attendees_purchase_names'),
        ('overview', 'attendees_purchase_confirm'),
        ('payment', 'attendees_payment'),
        ('done', 'attendees_purchase_done'),
    ])
    step = None

    def save_state(self, step=None):
        self.request.session['purchase_state'] = {
            'purchase_pk': self.purchase.pk,
            'previous_step': step if step is not None else self.step,
        }

    def get_previous_state(self):
        state = self.request.session.get('purchase_state')
        if state is None:
            return None
        self.previous_step = state['previous_step']
        if self.request.user.is_authenticated():
            self.purchase = get_object_or_404(Purchase,
                                              pk=state['purchase_pk'],
                                              user=self.request.user)
        else:
            self.purchase = get_object_or_404(Purchase,
                                              pk=state['purchase_pk'])
        return state

    def clear_purchase_info(self):
        if 'purchase_state' in self.request.session:
            del self.request.session['purchase_state']

    def setup(self):
        if self.step != 'start':
            steps = self.steps.keys()
            if not self.get_previous_state():
                return HttpResponseRedirect(
                    reverse(self.steps[self.steps.keys()[0]]))
            if steps.index(self.previous_step) < steps.index(self.step) - 1:
                next_step = steps[steps.index(self.previous_step) + 1]
                return HttpResponseRedirect(reverse(self.steps[next_step]))

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        resp = self.setup()
        if resp is not None:
            return resp
        return super(PurchaseMixin, self).dispatch(request, *args, **kwargs)


class StartPurchaseView(LoginRequiredMixin, PurchaseMixin, generic_views.View):
    step = 'start'
    form = None

    quantity_forms = None
    all_quantity_forms_valid = True
    total_ticket_num = 0

    def get(self, *args, **kwargs):
        self.clear_purchase_info()
        if self.form is None:
            self.form = forms.PurchaseForm(initial={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
            })
        if self.quantity_forms is None:
            self.quantity_forms = [
                forms.TicketQuantityForm(ticket_type=ticket_type)
                for ticket_type in TicketType.objects.available().select_related('vouchertype_needed')
            ]

        return render(self.request, 'attendees/purchase.html', {
            'no_tickets_selected': self.total_ticket_num < 1
            and self.request.POST,
            'quantity_forms': self.quantity_forms,
            'form': self.form,
            'step': self.step,
        })

    def post(self, *args, **kwargs):
        self.form = forms.PurchaseForm(self.request.POST)

        # Create a quantity for for each available ticket type.
        self.quantity_forms = []
        self.all_quantity_forms_valid = True
        self.total_ticket_num = 0
        for ticket_type in TicketType.objects.available():
            quantity_form = forms.TicketQuantityForm(
                data=self.request.POST,
                ticket_type=ticket_type)

            if quantity_form.is_valid():
                self.total_ticket_num += quantity_form.cleaned_data.get(
                    'quantity', 0)
            else:
                self.all_quantity_forms_valid = False

            self.quantity_forms.append(quantity_form)

        # Address, quantities (limits) and at least one ticket must be bought
        if self.form.is_valid() and self.all_quantity_forms_valid\
                and self.total_ticket_num > 0:
            purchase = self.form.save(commit=False)
            if self.request.user.is_authenticated():
                purchase.user = self.request.user
            purchase.save()

            # Create a ticket for each ticket type and amount
            for quantity_form in self.quantity_forms:
                for i in range(0,
                               quantity_form.cleaned_data.get('quantity', 0)):
                    Ticket.objects.create(
                        purchase=purchase,
                        ticket_type=quantity_form.ticket_type)
            self.purchase = purchase
            self.save_state()
            return redirect('attendees_purchase_names')

        return self.get(*args, **kwargs)


class PurchaseNamesView(LoginRequiredMixin, PurchaseMixin, generic_views.View):
    step = 'names'

    no_double_voucher = True
    name_forms = None
    voucher_forms = None

    def get(self, *args, **kwargs):
        if self.name_forms is None:
            self.name_forms = [
                forms.TicketNameForm(instance=ticket)
                for ticket in self.purchase.ticket_set.all()
            ]
        if self.voucher_forms is None:
            self.voucher_forms = [
                forms.TicketVoucherForm(instance=ticket)
                for ticket in self.purchase.ticket_set.filter(
                    ticket_type__vouchertype_needed__isnull=False)
            ]

        return render(self.request, 'attendees/purchase_names.html', {
            'name_forms': self.name_forms,
            'double_vouchers': not self.no_double_voucher
            and self.request.POST,
            'voucher_forms': self.voucher_forms,
            'step': self.step,
        })

    def post(self, *args, **kwargs):
        self.name_forms = []
        self.all_name_forms_valid = True
        for ticket in self.purchase.ticket_set.all():
            name_form = forms.TicketNameForm(
                data=self.request.POST, instance=ticket)

            if not name_form.is_valid():
                self.all_name_forms_valid = False

            self.name_forms.append(name_form)

        self.voucher_forms = []
        self.used_vouchers = []
        self.all_voucher_forms_valid = True

        for ticket in self.purchase.ticket_set.filter(
                ticket_type__vouchertype_needed__isnull=False):
            voucher_form = forms.TicketVoucherForm(
                data=self.request.POST, instance=ticket)

            if voucher_form.is_valid():
                if voucher_form.cleaned_data['code'] in self.used_vouchers:
                    self.no_double_voucher = False
                else:
                    self.used_vouchers.append(
                        voucher_form.cleaned_data['code'])
            else:
                self.all_voucher_forms_valid = False

            self.voucher_forms.append(voucher_form)

        # All name forms, voucher forms must be valid, voucher codes must not
        # be used twice
        if self.all_name_forms_valid and self.all_voucher_forms_valid\
                and self.no_double_voucher:
            for name_form in self.name_forms:
                name_form.save()
            for voucher_form in self.voucher_forms:
                voucher_form.save()

            # Redirect to confirm page.
            self.save_state()
            return redirect('attendees_purchase_confirm')
        return self.get(*args, **kwargs)


class PurchaseOverviewView(LoginRequiredMixin, PurchaseMixin,
                           generic_views.FormView):
    """
    This view renders all the order details and offers the user a choice of
    how to pay for the tickets.
    """
    template_name = 'attendees/purchase_confirm.html'
    form_class = forms.PurchaseOverviewForm
    step = 'overview'

    def get_context_data(self, *args, **kwargs):
        data = super(PurchaseOverviewView, self).get_context_data(*args,
                                                                  **kwargs)
        data['purchase'] = self.purchase
        data['step'] = self.step
        return data

    def form_valid(self, form):
        purchase = self.purchase
        purchase.payment_method = form.cleaned_data['payment_method']
        purchase.save()
        if purchase.payment_method == 'invoice':
            resp = utils.complete_purchase(purchase)
            self.save_state('payment')  # We can skip this step
            return resp
        else:
            self.save_state()
            return redirect('attendees_purchase_payment')


class HandlePaymentView(LoginRequiredMixin, PurchaseMixin,
                        generic_views.TemplateView):
    error = None
    step = 'payment'

    def get_template_names(self):
        return ['attendees/payment_paymill.html']

    def get_context_data(self, *args, **kwargs):
        data = super(HandlePaymentView, self).get_context_data(*args, **kwargs)
        data['public_key'] = settings.PAYMILL_PUBLIC_KEY
        data['amount_in_cent'] = int(
            decimal.Decimal(self.purchase.payment_total) * 100)
        this_year = datetime.datetime.now().year
        data['exp_years'] = range(this_year, this_year + 10)
        data['error'] = self.error
        data['purchase'] = self.purchase
        data['step'] = self.step
        return data

    def post(self, *args, **kwargs):
        purchase = self.purchase
        token = self.request.POST['token']
        api = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)
        try:
            resp = api.transact(
                amount=purchase.payment_total_in_cents,
                description=utils.generate_transaction_description(purchase),
                token=token
            )
        except Exception, e:
            LOG.exception("Failed to handle purchase")
            self.error = unicode(e)
            return self.get(*args, **kwargs)
        if resp is None:
            self.error = _("Payment failed. Please check your data.")
            return self.get(*args, **kwargs)
        else:
            transaction = resp
            if transaction.response_code != 20000:
                self.error = _(api.response_code2text(transaction.response_code))
                return self.get(*args, **kwargs)
            purchase.payment_transaction = transaction.id
            self.save_state()
            return utils.complete_purchase(purchase)


class ConfirmationView(LoginRequiredMixin, PurchaseMixin,
                       generic_views.TemplateView):
    template_name = 'attendees/purchase_done.html'
    step = 'done'

    def get_context_data(self, *args, **kwargs):
        self.clear_purchase_info()
        data = super(ConfirmationView, self).get_context_data(*args, **kwargs)
        data['step'] = self.step
        return data

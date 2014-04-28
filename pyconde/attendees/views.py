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
import logging
import hashlib
import json
from collections import OrderedDict

import pymill

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.auth import models as auth_models
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.response import TemplateResponse
import django.views.generic as generic_views

from pyconde.conference.models import current_conference
from braces.views import LoginRequiredMixin

from .models import TicketType, Ticket, VenueTicket, SIMCardTicket, Purchase
from .tasks import send_invoice
from . import forms
from . import utils
from . import exceptions


LOG = logging.getLogger(__name__)


class PurchaseMixin(object):
    """
    This is a general mixin that ensures that the right purchase is available
    and that the user doesn't jump ahead from view to view when not all
    the required steps have been visited.
    """
    steps = OrderedDict([
        ('start', 'attendees_purchase'),
        ('names', 'attendees_purchase_names'),
        ('overview', 'attendees_purchase_confirm'),
        ('payment', 'attendees_payment'),
        ('done', 'attendees_purchase_done'),
    ])
    step = None

    def __init__(self, *args, **kwargs):
        self.purchase = None
        self.tickets = []

    def save_state(self, step=None):
        # Warning: To keep the form interaction as simple as possible
        #          we are storing a temporary pk with each ticket if non
        #          has been set yet.
        if self.tickets:
            for idx, ticket in enumerate(self.tickets):
                if ticket.pk is None:
                    ticket.pk = idx
        expires = self.request.session.get('purchase_state', {}).get('expires')
        if expires is None:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=settings.MAX_CHECKOUT_DURATION)
        self.request.session['purchase_state'] = {
            'purchase': self.purchase,
            'previous_step': step if step is not None else self.step,
            'tickets': self.tickets,
            'expires': expires,
        }

    def get_previous_state(self):
        state = self.request.session.get('purchase_state')
        if state is None:
            return None
        if datetime.datetime.utcnow() > state['expires']:
            return None
        self.previous_step = state['previous_step']
        self.purchase = state['purchase']
        self.tickets = state.get('tickets', [])

        self.limited_tickets = []
        if self.step != 'done':
            # For steps before the confirmation we calculate the number of
            # available tickets to be rendered to the user. If we at this
            # point run into the situation that the requested quantity can
            # no longer be fulfilled, the checkout is aborted.
            ticket_types = {}
            for ticket in self.tickets:
                if ticket.ticket_type.pk not in ticket_types:
                    ticket_type = TicketType.objects.get(
                        pk=ticket.ticket_type.pk)
                    available = ticket_type.available_tickets
                    if available is None:
                        continue
                    if available <= 0:
                        raise exceptions.TicketNotAvailable(ticket_type)
                    ticket_types[ticket_type.pk] = {
                        'type': ticket_type,
                        'qty': 0,
                        'available': available
                    }
                ticket_types[ticket.ticket_type.pk]['qty'] += 1
            for _, ticket_type in ticket_types.items():
                if ticket_type['available'] - ticket_type['qty'] < 0:
                    raise exceptions.TicketNotAvailable(ticket_type['type'])
                self.limited_tickets.append(ticket_type)

        if self.request.user.is_authenticated():
            self.purchase.user = self.request.user
        return state

    def clear_purchase_info(self):
        if 'purchase_state' in self.request.session:
            del self.request.session['purchase_state']
        if 'paymentform' in self.request.session:
            del self.request.session['paymentform']
        self.tickets = []
        self.purchase = None
        self.previous_step = None

    def persist_purchase(self):
        # If we get into this method a second time because of a failed CC
        # payment, we have to remove all elements attached to this purchase
        # object and also reset things like the transaction ID.
        self.purchase.ticket_set.all().delete()
        self.purchase.payment_transaction = ""
        self.purchase.save()

        # Now we create the actual tickets (again)
        for ticket in self.tickets:
            # NOTE: At this point the ticket availability is decreased.
            #       This is corrected by the "purge_stale_purchases"
            #       command.
            #       Vouchers are invalidated by complete_purchase().
            ticket.pk = None
            ticket.purchase = self.purchase
            LOG.warning(str(ticket))
            ticket.save()

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
        try:
            resp = self.setup()
        except exceptions.TicketNotAvailable, e:
            messages.error(request, _("Sorry, the following ticket is no longer available in your requested quantity: %s" % e.ticket_type))
            return HttpResponseRedirect(
                reverse(self.steps[self.steps.keys()[0]]))
        if resp is not None:
            return resp
        return super(PurchaseMixin, self).dispatch(request, *args, **kwargs)


class StartPurchaseView(LoginRequiredMixin, PurchaseMixin, generic_views.View):
    """
    This first step of the checkout process presents the user with a list of
    available ticket types as well as a form to enter their payment address
    details.
    """
    step = 'start'
    form = None

    quantity_forms = None
    total_ticket_num = 0

    def get(self, *args, **kwargs):
        # TODO: If available (because a checkout was not finished) reuse the
        #       purchase object for initial data.
        self.clear_purchase_info()
        if self.form is None:
            self.form = forms.PurchaseForm(initial={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
            })

        ticket_types = TicketType.objects.available()\
            .filter(conference=current_conference)\
            .select_related('vouchertype_needed')
        if self.quantity_forms is None:
            self.quantity_forms = [
                forms.TicketQuantityForm(ticket_type=ticket_type)
                for ticket_type in ticket_types
            ]

        return render(self.request, 'attendees/purchase.html', {
            'no_tickets_selected': self.total_ticket_num < 1
            and self.request.POST,
            'quantity_forms': self.quantity_forms,
            'form': self.form,
            'step': self.step,
        })

    def post(self, *args, **kwargs):
        self.clear_purchase_info()
        self.form = forms.PurchaseForm(self.request.POST)

        # Create a quantity for for each available ticket type.
        self.quantity_forms = []
        all_quantity_forms_valid = True
        self.total_ticket_num = 0
        ticket_types = TicketType.objects.available().filter(
            conference=current_conference())
        for ticket_type in ticket_types:
            quantity_form = forms.TicketQuantityForm(
                data=self.request.POST,
                ticket_type=ticket_type)

            if quantity_form.is_valid():
                self.total_ticket_num += quantity_form.cleaned_data.get(
                    'quantity', 0)
            else:
                all_quantity_forms_valid = False

            self.quantity_forms.append(quantity_form)

        # Address, quantities (limits) and at least one ticket must be bought
        if self.form.is_valid() and all_quantity_forms_valid\
                and self.total_ticket_num > 0:
            purchase = self.form.save(commit=False)
            if self.request.user.is_authenticated():
                purchase.user = self.request.user
            purchase.conference = current_conference()

            # Create a ticket for each ticket type and amount
            for quantity_form in self.quantity_forms:
                for _i in range(0,
                                quantity_form.cleaned_data.get('quantity', 0)):
                    ticket_model = quantity_form.ticket_type.content_type.model_class()
                    self.tickets.append(
                        ticket_model(purchase=purchase,
                               ticket_type=quantity_form.ticket_type))
            purchase.payment_total = purchase.calculate_payment_total(
                tickets=self.tickets)
            self.purchase = purchase

            # Please note that we don't save the purchase object nor the
            # freshly created tickets yet but instead put them just into
            # the session.
            self.save_state()

            return redirect('attendees_purchase_names')

        return self.get(*args, **kwargs)


class PurchaseNamesView(LoginRequiredMixin, PurchaseMixin, generic_views.View):
    """
    The second step of the checkout offers the customer a form to enter
    details for the tickets themselves (first name, last name, ...) as well
    as provide a voucher form for tickets that require it.
    """
    step = 'names'

    no_double_voucher = True
    name_forms = None
    sim_forms = None
    voucher_forms = None

    def get(self, *args, **kwargs):
        if self.name_forms is None:
            self.name_forms = []
        if self.sim_forms is None:
            self.sim_forms = []
        if self.voucher_forms is None:
            self.voucher_forms = []

        for ticket in self.tickets:
            if isinstance(ticket, VenueTicket):
                name_form = forms.TicketNameForm(instance=ticket)
                self.name_forms.append(name_form)

            elif isinstance(ticket, SIMCardTicket):
                sim_form = forms.SIMCardNameForm(instance=ticket)
                self.sim_forms.append(sim_form)

            if ticket.ticket_type.vouchertype_needed is not None:
                voucher_form = forms.TicketVoucherForm(instance=ticket)
                self.voucher_forms.append(voucher_form)

        # Is there a way to redirect to the next page if there are no forms?
        # if not (self.name_forms or self.sim_forms or self.voucher_forms):
        #     # redirect if no forms exist
        #     return redirect('attendees_purchase_confirm')

        return render(self.request, 'attendees/purchase_names.html', {
            'name_forms': self.name_forms,
            'sim_forms': self.sim_forms,
            'double_vouchers': not self.no_double_voucher and self.request.POST,
            'voucher_forms': self.voucher_forms,
            'step': self.step,
            'limited_tickets': self.limited_tickets,
        })

    def post(self, *args, **kwargs):
        self.name_forms = []
        self.sim_forms = []
        self.voucher_forms = []
        self.used_vouchers = []
        self.all_voucher_forms_valid = True
        all_name_forms_valid = True
        all_sim_forms_valid = True

        for ticket in self.tickets:
            if isinstance(ticket, VenueTicket):
                name_form = forms.TicketNameForm(data=self.request.POST,
                    instance=ticket)
                self.name_forms.append(name_form)
                if not name_form.is_valid():
                    all_name_forms_valid = False
            elif isinstance(ticket, SIMCardTicket):
                sim_form = forms.SIMCardNameForm(data=self.request.POST,
                    instance=ticket)
                self.sim_forms.append(sim_form)
                if not sim_form.is_valid():
                    all_sim_forms_valid = False

            if ticket.ticket_type.vouchertype_needed is not None:
                voucher_form = forms.TicketVoucherForm(data=self.request.POST,
                    instance=ticket)
                voucher_form.request = self.request

                if voucher_form.is_valid():
                    code = voucher_form.cleaned_data['code']
                    if code in self.used_vouchers:
                        self.no_double_voucher = False
                    else:
                        self.used_vouchers.append(code)
                else:
                    self.all_voucher_forms_valid = False

                self.voucher_forms.append(voucher_form)

        # All name forms, voucher forms must be valid, voucher codes must not
        # be used twice
        if all_name_forms_valid and all_sim_forms_valid \
                and self.all_voucher_forms_valid \
                and self.no_double_voucher:
            for idx, name_form in enumerate(self.name_forms):
                self.tickets[idx] = name_form.save(commit=False)
            for idx, sim_form in enumerate(self.sim_forms):
                self.sim_forms[idx] = sim_form.save(commit=False)
            for voucher_form in self.voucher_forms:
                voucher_form.save(commit=False)

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

    def get_form_kwargs(self):
        result = super(PurchaseOverviewView, self).get_form_kwargs()
        result['purchase'] = self.purchase
        return result

    def get_context_data(self, *args, **kwargs):
        data = super(PurchaseOverviewView, self).get_context_data(*args,
                                                                  **kwargs)
        data['purchase'] = self.purchase
        data['step'] = self.step
        data['tickets'] = self.tickets
        data['limited_tickets'] = self.limited_tickets
        return data

    def form_valid(self, form):
        purchase = self.purchase
        purchase.payment_method = form.cleaned_data['payment_method']
        if purchase.payment_method == 'invoice':
            self.persist_purchase()
            resp = utils.complete_purchase(self.request, purchase)
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
        data['amount_in_cent'] = self.purchase.payment_total_in_cents
        this_year = now().year
        data['exp_years'] = range(this_year, this_year + 10)
        data['error'] = self.error
        data['purchase'] = self.purchase
        data['step'] = self.step
        return data

    def clean_purchase(self, purchase):
        """
        We have to reset the paymentform session element to allow a
        resubmission of the payment form in case of an error during a prior
        attempt.
        """
        del self.request.session['paymentform']

    def post(self, *args, **kwargs):
        purchase = self.purchase
        token = self.request.POST['token']
        # generate hash on purchase and store in session to avoid double POST
        # of payment form for same user/purchase (note that different tokens
        # may be generated in case of parallel POST of payment form)
        # To have all the data available for the generation we finally have
        # to save the purchase object and the associated tickets.
        self.persist_purchase()
        paymenthash = hashlib.md5()
        paymenthash.update("{0}:{1}".format(purchase.conference.pk,
                                            purchase.pk))
        paymenthash = paymenthash.hexdigest()

        if (self.request.session.get('paymentform') != paymenthash
                and not purchase.payment_transaction):
            self.request.session['paymentform'] = paymenthash
            purchase.payment_transaction = paymenthash
            purchase.save()
            api = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)
            try:
                resp = api.transact(
                    amount=purchase.payment_total_in_cents,
                    description=utils.generate_transaction_description(purchase),
                    token=token
                )
            except Exception, e:
                LOG.exception("Failed to handle purchase")
                self.clean_purchase(purchase)
                self.error = unicode(e)
                return self.get(*args, **kwargs)
            if resp is None:
                self.clean_purchase(purchase)
                self.error = _("Payment failed. Please check your data.")
                return self.get(*args, **kwargs)
            else:
                transaction = resp
                if transaction.response_code != 20000:
                    self.clean_purchase(purchase)
                    self.error = _(api.response_code2text(transaction.response_code))
                    return self.get(*args, **kwargs)
                purchase.payment_transaction = transaction.id
                self.save_state()
                return utils.complete_purchase(self.request, purchase)
        else:
            if purchase.payment_transaction:
                self.error = _("Transaction already processed.")  # + purchase.payment_transaction
            else:
                self.error = _("Purchase already handled.")
            return self.get(*args, **kwargs)


class ConfirmationView(LoginRequiredMixin, PurchaseMixin,
                       generic_views.TemplateView):
    template_name = 'attendees/purchase_done.html'
    step = 'done'

    def get_context_data(self, *args, **kwargs):
        self.clear_purchase_info()
        data = super(ConfirmationView, self).get_context_data(*args, **kwargs)
        data['step'] = self.step
        return data


class UserPurchasesView(LoginRequiredMixin, generic_views.TemplateView):
    """
    This view lists all the purchases done by the currently logged-in user.
    """
    template_name = 'attendees/user_purchases.html'

    def get_context_data(self):
        return {
            'tickets': Ticket.objects
                             .filter(purchase__user=self.request.user)
                             .exclude(purchase__state='incomplete')
                             .exclude(purchase__state='new')
                             .select_related('purchase', 'purchase__user',
                                             'ticket_type__content_type',
                                             'user')
                             .order_by('-purchase__date_added')
        }


class UserTicketsView(LoginRequiredMixin, generic_views.TemplateView):
    """
    This view provides the currently logged in user a list of all tickets
    associated with their account. If the user is also the one that purchased
    the ticket, they can reassign them to another user.
    """
    template_name = 'attendees/user_tickets.html'

    def get_context_data(self):
        return {
            'tickets': Ticket.objects
                             .get_active_user_tickets(self.request.user)
                             .select_related('ticket_type__content_type')
                             .filter(
                                 Q(ticket_type__content_type__app_label='attendees',
                                   ticket_type__content_type__model='venueticket') |
                                 Q(ticket_type__content_type__app_label='attendees',
                                   ticket_type__content_type__model='simcardticket')
                                 )
                             .all()
        }


class EditTicketView(LoginRequiredMixin, generic_views.UpdateView):
    """
    Through the EditTicketView the owner of a ticket can edit certain details
    of it. Note that this is limited to VenueTickets as this is intended to
    allow users to customize the information printed onto the ticket after the
    purchase has been made.
    """
    model = VenueTicket
    form_class = forms.EditVenueTicketForm
    template_name = 'attendees/edit_ticket.html'

    def get_object(self, queryset=None):
        obj = super(EditTicketView, self).get_object(queryset)
        if not obj.can_be_edited_by(self.request.user):
            raise Http404()
        return obj

    def get_success_url(self):
        return reverse('attendees_user_tickets')


class UserResendInvoiceView(LoginRequiredMixin, generic_views.View):
    """
    This view triggers a sending of the specified invoice.
    """

    http_method_names = ['post']

    def post(self, request):
        try:
            purchase_id = int(request.POST.get('p'))
            p = Purchase.objects.get(id=purchase_id, exported=True,
                 user=request.user)
            send_invoice(p.id, (p.email_receiver,))
            messages.success(request,
                _('The invoice has been sent to you.'))
        except (Purchase.DoesNotExist, KeyError, ValueError):
            messages.error(request,
                _('The invoice for this purchase does not exist or has not '
                  'yet been generated. You will receive a mail with the '
                  'invoice soon.'))
        return HttpResponseRedirect(reverse('attendees_user_purchases'))


class AssignTicketView(LoginRequiredMixin, generic_views.View):
    """
    This view allows the current user to assign a ticket from one of their
    purchases to a different user.
    """

    def dispatch(self, *args, **kwargs):
        self.ticket = get_object_or_404(
            Ticket,
            pk=kwargs['pk'], purchase__user=self.request.user,
            user__isnull=True, purchase__state='payment_received')
        return super(AssignTicketView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not hasattr(self, 'form'):
            self.form = forms.TicketAssignmentForm(
                current_user=self.request.user)
        return TemplateResponse(self.request, 'attendees/assign_ticket.html', {
            'form': self.form
            })

    def post(self, *args, **kwargs):
        self.form = forms.TicketAssignmentForm(
            data=self.request.POST, current_user=self.request.user)
        if self.form.is_valid():
            user = auth_models.User.objects.get(
                username=self.form.cleaned_data['username'])
            self.ticket.user = user
            self.ticket.save()
            messages.success(
                self.request,
                _("This ticket was successfully assigned to the specified user"))
            return HttpResponseRedirect(reverse('attendees_user_purchases'))
        return self.get(*args, **kwargs)


class AdminListTicketFieldsView(generic_views.View):
    """
    This view returns a JSON list of all the fields that are provided by
    the field and should be checked against in the admin.
    """
    def get(self, request, pk):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        ctype = get_object_or_404(ContentType.objects, pk=pk).model_class()
        if not issubclass(ctype, Ticket):
            raise Http404()
        result = [{'name': name, 'label': unicode(ctype._meta.get_field(name).verbose_name)} for name in ctype.get_fields()]
        return HttpResponse(json.dumps(result),
                content_type='text/json')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
import uuid

from functools import reduce
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core import signing
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models, transaction
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from ..attendees.models import (Purchase, Ticket, TicketType, SIMCardTicket,
    SupportTicket, VenueTicket)
from ..attendees.tasks import render_invoice
from ..attendees.utils import generate_invoice_number
from ..conference.models import current_conference
from .forms import (OnDeskPurchaseForm, OnDeskTicketForm,
    BaseOnDeskTicketFormSet, SearchForm)


class CheckinViewMixin(object):
    @method_decorator(permission_required('accounts.see_checkin_info'))
    def dispatch(self, *args, **kwargs):
        return super(CheckinViewMixin, self).dispatch(*args, **kwargs)


class SearchFormMixin(object):
    def get_context_data(self, **kwargs):
        context = super(SearchFormMixin, self).get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        return context


class SearchView(CheckinViewMixin, SearchFormMixin, ListView):
    template_name = 'checkin/search.html'
    model = Ticket
    context_object_name = 'results'
    search_fields = (
        'user__id',
        'user__username',
        'user__email',
        'user__profile__full_name',
        'user__profile__display_name',
        'id',
        'purchase__id',
        'purchase__company_name',
        'purchase__first_name',
        'purchase__last_name',
        'purchase__email',
        'purchase__invoice_number',
        'purchase__user__id',
        'purchase__user__username',
        'purchase__user__email',
        'purchase__user__profile__full_name',
        'purchase__user__profile__display_name',
        'simcardticket__first_name',
        'simcardticket__last_name',
        'venueticket__first_name',
        'venueticket__last_name',
    )

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['searched'] = 'query' in self.request.GET
        return context

    def get_queryset(self):
        if 'query' in self.request.GET:
            queryset = self.model.objects.select_related(
                'user',
                'user__profile',
                'purchase',
                'purchase__user',
                'purchase__user__profile',
                'simcardticket',
                'venueticket',
                'ticket_type',
                'ticket_type__content_type',
            ).filter(
                models.Q(simcardticket__isnull=False) |
                models.Q(venueticket__isnull=False)
            )
            terms = self.request.GET['query'].split()
            for term in terms:
                queries = [
                    models.Q(**{search_field + '__icontains': term})
                    for search_field in self.search_fields
                ]
                queryset = queryset.filter(reduce(operator.or_, queries))
            return queryset
        return []

    def get(self, *args, **kwargs):
        if 'query' in self.request.GET:
            self.search_terms = self.request.GET['query'].split()
        else:
            self.search_terms = []
        tickets = self.get_queryset()
        self.object_list = []
        for ticket in tickets:
            obj = {
                'ticket': {
                    'id': ticket.id,
                }
            }
            if ticket.user is None:
                obj['ticket'].update({
                    'full_name': ticket.real_ticket.first_name + ' ' + ticket.real_ticket.last_name,
                    'organisation': getattr(ticket.real_ticket, 'organisation', None)
                })
            else:
                obj['ticket'].update({
                    'user_id': ticket.user_id,
                    'username': ticket.user.username,
                    'email': ticket.user.email,
                    'full_name': ticket.user.profile.full_name,
                    'display_name': ticket.user.profile.display_name,
                    'organisation': ticket.user.profile.organisation
                })
            obj['purchase'] = {
                'id': ticket.purchase.id,
                'company_name': ticket.purchase.company_name,
                'invoice_number': ticket.purchase.invoice_number,
                'name': ticket.purchase.first_name + ' ' + ticket.purchase.last_name,
                'email': ticket.purchase.email
            }
            obj['buyer'] = {
                'user_id': ticket.purchase.user_id,
                'username': ticket.purchase.user.username,
                'email': ticket.purchase.user.email,
                'full_name': ticket.purchase.user.profile.full_name,
                'display_name': ticket.purchase.user.profile.display_name,
                'organisation': ticket.purchase.user.profile.organisation
            }

            self.object_list.append(obj)
        context = self.get_context_data(
            search_terms=self.search_terms,
            object_list=self.object_list
        )
        return self.render_to_response(context)

search_view = SearchView.as_view()


class OnDeskPurchaseView(CheckinViewMixin, SearchFormMixin, FormView):
    form_class = OnDeskPurchaseForm
    salt = 'pyconde.checkin.purchase'
    stage = 'form'
    template_name = 'checkin/ondesk_purchase_form.html'
    template_name_preview = 'checkin/ondesk_purchase_form_preview.html'
    ticket_formset_class = BaseOnDeskTicketFormSet
    ticket_form_class = OnDeskTicketForm
    timeout = 15*60  # seconds after which the preview timed out

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = formset_factory(self.ticket_form_class,
                                        formset=self.ticket_formset_class,
                                        extra=1)
        formset = formset_class()
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))

    def post(self, request, *args, **kwargs):
        if not self.request.POST.get('signed_data', None):
            self.start_session()

            # We perform the preview
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            formset_class = formset_factory(self.ticket_form_class,
                                            formset=self.ticket_formset_class,
                                            extra=1)
            formset = formset_class(data=self.request.POST)
            valid = (form.is_valid(), formset.is_valid(),)
            if all(valid):
                return self.form_valid(form, formset)
            else:
                return self.form_invalid(form, formset)
        else:
            # Verify existing session
            if not self.verify_session():
                messages.error(request, _('Purchase session timeout or purchase already processed'))
                return HttpResponseRedirect(reverse('checkin_purchase'))

            # We do the actual submit
            return self.form_post()

    def form_post(self):
        # Do the actual booking process. We already verified the data in
        # the preview step, and use the data from signed data package.
        self.stage = 'post'

        signed_data = self.request.POST.get('signed_data')
        try:
            data = signing.loads(signed_data, salt=self.salt, max_age=self.timeout)
            with transaction.commit_manually():
                # TODO:
                #   set form.email to some value
                try:
                    purchase = Purchase(**data['purchase'])
                    purchase.conference = current_conference()
                    purchase.state = 'new'
                    purchase.payment_method = 'invoice'
                    purchase.save()

                    for td in data['tickets']:
                        ticket_type = TicketType.objects.select_related('content_type') \
                                                        .get(id=td['ticket_type_id'])
                        TicketClass = ticket_type.content_type.model_class()
                        ticket = TicketClass(**td)
                        ticket.purchase = purchase
                        ticket.save()
                    purchase.payment_total = purchase.calculate_payment_total()
                    purchase.save(update_fields=['payment_total'])
                    purchase.invoice_number = generate_invoice_number()
                    purchase.save(update_fields=['invoice_number'])
                    self.object = purchase
                except Exception as e:
                    print(e)
                    transaction.rollback()
                    messages.error(self.request, _('An error occured while processing the purchase'))
                    return HttpResponseRedirect(reverse('checkin_purchase'))
                else:
                    # Delete the purchase_key first in case a database error occurs
                    del self.request.session['purchase_key']
                    transaction.commit()
                    messages.success(self.request, _('Purchase successful!'))
                    render_invoice.delay(purchase_id=purchase.id,
                                         send_purchaser=False)
                    return HttpResponseRedirect(self.get_success_url())
        except signing.SignatureExpired:
            messages.error(self.request, _('Session timed out. Please restart the purchase process.'))
        except signing.BadSignature:
            messages.error(self.request, _('Invalid data. Please restart the purchase process.'))
        return HttpResponseRedirect(reverse('checkin_purchase'))

    def form_valid(self, form, formset):
        # We allow users to preview their purchase.
        # We serialize all form data into one json object that is then
        # signed using django.core.signing
        self.stage = 'preview'

        serialized_data = self.serialize(form, formset)
        signed_data = signing.dumps(serialized_data, salt=self.salt, compress=True)

        purchase = form.cleaned_data
        tickets = []
        payment_total = 0.0
        for tform in formset.changed_forms:
            t = tform.cleaned_data
            # Copy for template access
            t['ticket_type'] = t['ticket_type_id']
            t['user'] = t['user_id']
            t['sponsor'] = t['sponsor_id']
            payment_total += t['ticket_type_id'].fee
            tickets.append(t)

        purchase['payment_total'] = payment_total

        ctx = self.get_context_data(signed_data=signed_data,
                                    purchase=purchase,
                                    tickets=tickets)
        return self.render_to_response(ctx)

    def form_invalid(self, form, formset):
        ctx = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(ctx)

    def get_context_data(self, **kwargs):
        ctx = super(OnDeskPurchaseView, self).get_context_data(**kwargs)
        ctx['purchase_key'] = self.request.session.get('purchase_key')
        if self.stage == 'preview':
            pass
        else:
            ctx['empty_form'] = ctx['formset'].empty_form
        return ctx

    def get_success_url(self):

        return reverse('checkin_purchase_detail', kwargs={'pk': self.object.pk})

    def get_template_names(self):
        if self.stage == 'preview':
            return [self.template_name_preview]
        return super(OnDeskPurchaseView, self).get_template_names()

    def serialize(self, form, formset):
        data = {}
        data['purchase'] = {bf.name: bf.data for bf in form}
        ticket_data = []
        for tf in formset.changed_forms:
            ticket_data.append({bf.name: bf.data for bf in tf})
        data['tickets'] = ticket_data
        return data

    def start_session(self):
        # Start new purchase session
        self.request.session['purchase_key'] = force_text(uuid.uuid4())

    def verify_session(self):
        # A session is only valid if the key exists in the POST data and the
        # session and the key is not None or ''
        purchase_key_session = self.request.session.get('purchase_key', None)
        purchase_key = self.request.POST.get('purchase_key', None)
        return purchase_key and purchase_key_session == purchase_key

purchase_view = OnDeskPurchaseView.as_view()


class OnDeskPurchaseDetailView(CheckinViewMixin, SearchFormMixin, DetailView):
    model = Purchase
    template_name = 'checkin/ondesk_purchase_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(OnDeskPurchaseDetailView, self).get_context_data(**kwargs)
        venues = VenueTicket.objects.filter(purchase_id=self.object.id).all()
        sims = SIMCardTicket.objects.filter(purchase_id=self.object.id).all()
        sups = SupportTicket.objects.filter(purchase_id=self.object.id).all()
        ctx['tickets'] = chain(venues, sims, sups)
        return ctx

    def get_queryset(self):
        qs = super(OnDeskPurchaseDetailView, self).get_queryset()
        qs = qs.select_related('ticket_set__ticket_type__content_type')
        return qs

purchase_detail_view = OnDeskPurchaseDetailView.as_view()

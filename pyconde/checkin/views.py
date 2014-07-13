# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
import uuid

from functools import reduce
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth.decorators import permission_required
from django.core import signing
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from django.views.generic import DetailView, FormView, ListView
from django.views.decorators.http import require_POST

from ..attendees.exporters import BadgeExporter
from ..attendees.models import (Purchase, Ticket, TicketType, SIMCardTicket,
    SupportTicket, VenueTicket)
from ..attendees.tasks import render_invoice
from ..attendees.utils import generate_invoice_number
from ..conference.models import current_conference

from .exporters import generate_badge
from .forms import (OnDeskPurchaseForm, EditOnDeskTicketForm,
    NewOnDeskTicketForm, BaseOnDeskTicketFormSet, SearchForm, get_users,
    get_sponsors)


def ctype(obj):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj)


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
            if ticket.purchase.user_id:
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
    ticket_form_class = NewOnDeskTicketForm
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
                    LogEntry.objects.log_action(
                        user_id=self.request.user.pk,
                        content_type_id=ctype(purchase).pk,
                        object_id=purchase.pk,
                        object_repr=force_text(purchase),
                        action_flag=ADDITION,
                        change_message='Checkin: Purchase created'
                    )
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
        ctx['stage'] = self.stage
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


@permission_required('accounts.see_checkin_info')
def purchase_invoice_view(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if purchase.exported:
        response = HttpResponse(content_type='application/pdf')

        ext = '.json' if settings.PURCHASE_INVOICE_DISABLE_RENDERING else '.pdf'
        filename = '%s%s' % (purchase.full_invoice_number, ext)
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        with open(purchase.invoice_filepath, 'rb') as f:
            response.write(f.read())
        return response
    else:
        messages.error(request, _('Invoice not yet exported.'))
        url = reverse('checkin_purchase_detail', kwargs={'pk': purchase.pk})
        return HttpResponseRedirect(url)


@permission_required('accounts.see_checkin_info')
def purchase_badges_view(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    tickets = VenueTicket.objects.filter(purchase_id=purchase.pk)
    return ticket_badge_view(request, tickets)


@require_POST
@permission_required('accounts.see_checkin_info')
def purchase_update_state(request, pk, new_state):
    purchase = get_object_or_404(Purchase, pk=pk)
    states = {
        'paid': 'payment_received',
        'unpaid': 'invoice_created',
        'cancel': 'canceled',
    }
    state = states.get(new_state, None)
    if state:
        old_state = purchase.state
        purchase.state = state
        purchase.save(update_fields=['state'])
        messages.success(request, _('Purchase marked as %(state)s.') % {
                         'state': new_state})
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ctype(purchase).pk,
            object_id=purchase.pk,
            object_repr=force_text(purchase),
            action_flag=CHANGE,
            change_message='Checkin: state changed from %s to %s' % (old_state, state)
        )
    else:
        messages.warning(request, _('Invalid state.'))
    url = reverse('checkin_purchase_detail', kwargs={'pk': purchase.pk})
    return HttpResponseRedirect(url)


class OnDeskTicketUpdateView(CheckinViewMixin, SearchFormMixin, FormView):
    form_class = EditOnDeskTicketForm
    model = VenueTicket
    template_name = 'checkin/ondesk_ticket_form.html'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(self.model, pk=kwargs.get('pk'))
        return super(OnDeskTicketUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(self.model, pk=kwargs.get('pk'))
        return super(OnDeskTicketUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        for k, v in form.cleaned_data.items():
            setattr(self.object, k, v)
        self.object.save(update_fields=form.cleaned_data.keys())
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ctype(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_text(self.object),
            action_flag=CHANGE,
            change_message='Checkin: %s' % ', '. join(
                '%s changed to %s' % (k, form.cleaned_data[k])
                for k in form.changed_data
            )
        )
        messages.success(self.request, _('Ticket sucessfully updated.'))
        return super(OnDeskTicketUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(OnDeskTicketUpdateView, self).get_form_kwargs()
        kwargs.update({
            'users': get_users(),
            'sponsors': get_sponsors()
        })
        return kwargs

    def get_initial(self):
        return {
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'organisation': self.object.organisation,
            'user_id': self.object.user_id,
            'sponsor_id': self.object.sponsor_id,
        }

    def get_success_url(self):
        return reverse('checkin_purchase_detail', kwargs={'pk': self.object.purchase.pk})

ticket_update_view = OnDeskTicketUpdateView.as_view()


@permission_required('accounts.see_checkin_info')
def ticket_badge_view(request, pk):
    if isinstance(pk, models.query.QuerySet):
        ticket = pk
    else:
        ticket = VenueTicket.objects.filter(pk=pk)

    ticket = ticket.filter(canceled=False)

    count = ticket.count()
    if count == 0:
        raise Http404

    be = BadgeExporter(ticket, 'https://ep14.org/u{uid}', indent=False)
    data = be.export()
    pdf = generate_badge(data)
    if pdf is not None:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="badge.pdf"'
        response.write(pdf)
        return response
    else:
        msg = ungettext_lazy('Error generating the badge',
                             'Error generating the badges',
                             count)
        messages.error(request, msg)
        url = reverse('checkin_purchase_detail', kwargs={'pk': ticket[0].purchase_id})
        return HttpResponseRedirect(url)

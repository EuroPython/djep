# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
from functools import reduce

from django.db import models
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from ..attendees.models import Ticket
from .forms import SearchForm


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

# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from pyconde.attendees.models import TicketType, Ticket, Purchase, PURCHASE_STATES
from pyconde.attendees.forms import PurchaseForm, TicketQuantityForm, TicketNameForm, TicketVoucherForm


@login_required
def purchase(request):
    total_ticket_num = 0

    if request.method == 'POST':
        form = PurchaseForm(request.POST)

        # Create a quantity for for each available ticket type.
        quantity_forms = []
        all_quantity_forms_valid = True
        for ticket_type in TicketType.objects.available():
            quantity_form = TicketQuantityForm(data=request.POST,
                ticket_type=ticket_type)

            if quantity_form.is_valid():
                total_ticket_num += quantity_form.cleaned_data.get('quantity', 0)
            else:
                all_quantity_forms_valid = False

            quantity_forms.append(quantity_form)

        # Address, quantities (limits) and at least one ticket must be bought
        if form.is_valid() and all_quantity_forms_valid and total_ticket_num > 0:
            purchase = form.save()

            # Create a ticket for each ticket type and amount
            for quantity_form in quantity_forms:
                for i in range(0, quantity_form.cleaned_data.get('quantity', 0)):
                    Ticket.objects.create(purchase=purchase,
                        ticket_type=quantity_form.ticket_type)

            # Redirect to names page
            return redirect('attendees_purchase_names', pk=purchase.pk)
    else:
        form = PurchaseForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        quantity_forms = [TicketQuantityForm(ticket_type=ticket_type)
            for ticket_type in TicketType.objects.available()]

    return render(request, 'attendees/purchase.html', {
        'no_tickets_selected': total_ticket_num < 1 and request.POST,
        'quantity_forms': quantity_forms,
        'form': form,
    })


@login_required
def purchase_names(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, state='incomplete')

    no_double_voucher = True

    if request.method == 'POST':
        name_forms = []
        all_name_forms_valid = True
        for ticket in purchase.ticket_set.all():
            name_form = TicketNameForm(data=request.POST, instance=ticket)

            if not name_form.is_valid():
                all_name_forms_valid = False

            name_forms.append(name_form)

        voucher_forms = []
        used_vouchers = []
        all_voucher_forms_valid = True
        for ticket in purchase.ticket_set.filter(ticket_type__voucher_needed=True):
            voucher_form = TicketVoucherForm(data=request.POST, instance=ticket)

            if voucher_form.is_valid():
                if voucher_form.cleaned_data['code'] in used_vouchers:
                    no_double_voucher = False
                else:
                    used_vouchers.append(voucher_form.cleaned_data['code'])
            else:
                all_voucher_forms_valid = False

            voucher_forms.append(voucher_form)

        # All name forms, voucher forms must be valid, voucher codes must not be used twice
        if all_name_forms_valid and all_voucher_forms_valid and no_double_voucher:
            for name_form in name_forms:
                name_form.save()
            for voucher_form in voucher_forms:
                voucher_form.save()

            # Redirect to confirm page.
            return redirect('attendees_purchase_confirm', pk=purchase.pk)
    else:
        name_forms = [TicketNameForm(instance=ticket)
            for ticket in purchase.ticket_set.all()]
        voucher_forms = [TicketVoucherForm(instance=ticket)
            for ticket in purchase.ticket_set.filter(
                ticket_type__voucher_needed=True)]

    return render(request, 'attendees/purchase_names.html', {
        'name_forms': name_forms,
        'double_vouchers': not no_double_voucher and request.POST,
        'voucher_forms': voucher_forms
    })


@login_required
def purchase_confirm(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, state='incomplete')

    if request.method == 'POST':
        purchase.state = 'new'
        purchase.save()

        send_mail(_('Ticket successfully purchased'),
            render_to_string('attendees/mail_purchase_completed.html', {
                'purchase': purchase
            }),
            settings.DEFAULT_FROM_EMAIL,
            [purchase.customer.email, settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )

        # Redirect to thank you page.
        return redirect('attendees_purchase_done')

    return render(request, 'attendees/purchase_confirm.html', {
        'purchase': purchase,
    })

# -* coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from pyconde.attendees.models import (Customer, Purchase, Ticket, TicketType,
    Voucher)


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('product_number', '__unicode__', 'fee', 'is_active',
        'voucher_needed', 'tutorial_ticket', 'purchases_count',
        'max_purchases', 'date_valid_from', 'date_valid_to')
    list_display_links = ('product_number', '__unicode__')
    list_filter = ('is_active',)

admin.site.register(TicketType, TicketTypeAdmin)


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'remarks', 'is_used', 'date_valid')
    list_filter = ('is_used',)
    search_fields = ('code', 'remarks')

admin.site.register(Voucher, VoucherAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'email', 'date_added', 'is_exported')
    list_filter = ('is_exported',)
    search_fields = ('email',)

admin.site.register(Customer, CustomerAdmin)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'payment_total', 'first_name', 'last_name',
        'company_name', 'street', 'city', 'date_added', 'state')
    list_editable = ('state',)
    list_filter = ('state', 'date_added')
    inlines = [TicketInline]
    actions = ['send_confirmation']

    def send_confirmation(self, request, queryset):
        sent = 0
        for purchase in queryset.filter(
            state__in=('invoice_created', 'payment_received')):

            send_mail('Bestätigung des Zahlungseingangs',
                render_to_string('attendees/mail_payment_received.html', {
                    'purchase': purchase
                }),
                settings.DEFAULT_FROM_EMAIL,
                [purchase.customer.email, settings.DEFAULT_FROM_EMAIL],
                fail_silently=True
            )
            if purchase.state == 'invoice_created':
                purchase.state = 'payment_received'
                purchase.save()
            sent += 1

        if sent == 1:
            message_bit = _('1 mail was')
        else:
            message_bit = _('%s mails were') % sent

        self.message_user(request, _('%s successfully sent.') % message_bit)
    send_confirmation.short_description = _(
        'Send confirmation for selected %(verbose_name_plural)s')

admin.site.register(Purchase, PurchaseAdmin)


class TicketAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'first_name', 'last_name', 'ticket_type', 'date_added')
    list_filter = ('ticket_type', 'date_added', 'purchase__state')
    search_fields = ('first_name', 'last_name', 'purchase__customer__email')

admin.site.register(Ticket, TicketAdmin)

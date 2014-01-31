# -* coding: utf-8 -*-
from __future__ import unicode_literals

from email.utils import formataddr

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext, ugettext_lazy as _

from . import tasks
from . import utils
from .models import Purchase, Ticket, TicketType, Voucher, VoucherType, TShirtSize


def export_tickets(modeladmin, request, queryset):
    return HttpResponse(utils.create_tickets_export(queryset).csv, mimetype='text/csv')
export_tickets.short_description = _("Export as CSV")


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('product_number', '__unicode__', 'conference',
                    'fee', 'is_active', 'tutorial_ticket', 'purchases_count',
                    'max_purchases', 'date_valid_from', 'date_valid_to')
    list_display_links = ('product_number', '__unicode__')
    list_filter = ('is_active', 'conference')

admin.site.register(TicketType, TicketTypeAdmin)


class ShirtSizeAdmin(admin.ModelAdmin):
    list_display = ('size', 'sort')

admin.site.register(TShirtSize, ShirtSizeAdmin)


class VoucherTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference')
    list_filter = ('conference',)


admin.site.register(VoucherType, VoucherTypeAdmin)


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('pk', 'code', 'is_used', 'type', 'remarks', 'date_valid')
    list_filter = ('is_used', 'type')
    search_fields = ('code', 'remarks')

admin.site.register(Voucher, VoucherAdmin)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'full_invoice_number', 'pk', 'payment_total', 'first_name', 'last_name',
        'company_name', 'street', 'city', 'date_added', 'payment_method',
        'state', 'exported', 'conference',
    )
    list_editable = ('state',)
    list_filter = ('state', 'date_added', 'payment_method', 'exported',
                   'conference',)
    inlines = [TicketInline]
    actions = ['send_payment_confirmation', 'export_and_send_invoices',
               'send_invoice_to_myself', 'send_invoice_to_customer']

    def export_and_send_invoices(self, request, queryset):
        for purchase in queryset:
            if not purchase.exported:
                tasks.render_invoice.delay(purchase.pk)
            else:
                self.message_user(request,
                    _('Purchase %(invoice_number)s has already been exported. '
                      'Use “Send me a copy of the invoice” or “Send customer '
                      'a copy of the invoice” to mail the invoice.') % {
                        'invoice_number': purchase.full_invoice_number,
                    })
    export_and_send_invoices.short_description = _('Export invoice and send')

    def send_invoice_to_myself(self, request, queryset):
        recipients = (request.user.email,)  # Needs a tuple
        for purchase in queryset:
            if purchase.exported:
                tasks.send_invoice.delay(purchase.pk, recipients)
            else:
                self.message_user(request,
                    _('Purchase %(invoice_number)s has not been exported yet. '
                      'Use “Export invoice and send” to export the invoice '
                      'and send it to the customer.') % {
                        'invoice_number': purchase.full_invoice_number,
                    })
    send_invoice_to_myself.short_description = _('Send me a copy of the invoice')

    def send_invoice_to_customer(self, request, queryset):
        for purchase in queryset:
            if purchase.exported:
                name = "%s %s" % (purchase.first_name, purchase.last_name)
                recipients = (formataddr((name, purchase.email)),)  # Needs a tuple
                tasks.send_invoice.delay(purchase.pk, recipients)
            else:
                self.message_user(request,
                    _('Purchase %(invoice_number)s has not been exported yet. '
                      'Use “Export invoice and send” to export the invoice '
                      'and send it to the customer.') % {
                        'invoice_number': purchase.full_invoice_number,
                    })
    send_invoice_to_customer.short_description = _('Send customer a copy of the invoice')

    def send_payment_confirmation(self, request, queryset):
        sent = 0
        for purchase in queryset.filter(
                state__in=('invoice_created', 'payment_received')):

            send_mail(ugettext('Payment receipt confirmation'),
                render_to_string('attendees/mail_payment_received.html', {
                    'purchase': purchase,
                    'conference': purchase.conference
                }),
                settings.DEFAULT_FROM_EMAIL,
                [purchase.email, settings.DEFAULT_FROM_EMAIL],
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

        self.message_user(request, ugettext('%s successfully sent.') % message_bit)
    send_payment_confirmation.short_description = _(
        'Send payment confirmation for selected %(verbose_name_plural)s')

admin.site.register(Purchase, PurchaseAdmin)


class TicketAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'first_name', 'last_name', 'ticket_type',
                    'shirtsize', 'date_added')
    list_filter = ('ticket_type', 'date_added', 'purchase__state')
    search_fields = ('first_name', 'last_name', 'purchase__email')
    actions = [export_tickets]

admin.site.register(Ticket, TicketAdmin)

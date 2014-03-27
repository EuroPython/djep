# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

from . import views


urlpatterns = patterns(
    'pyconde.attendees.views',
    url(r'^$', views.StartPurchaseView.as_view(),
        name='attendees_purchase'),
    url(r'^names/$', views.PurchaseNamesView.as_view(),
        name='attendees_purchase_names'),
    url(r'^confirm/$', views.PurchaseOverviewView.as_view(),
        name='attendees_purchase_confirm'),
    url(r'^done/$', views.ConfirmationView.as_view(),
        name='attendees_purchase_done'),
    url(r'^payment/$', views.HandlePaymentView.as_view(),
        name='attendees_purchase_payment'),
    url(r'^mine/$', views.UserPurchasesView.as_view(),
        name='attendees_user_purchases'),
    url(r'^mine/tickets/$', views.UserTicketsView.as_view(),
        name='attendees_user_tickets'),
    url(r'^mine/tickets/assign/(?P<pk>\d+)/$',
        views.AssignTicketView.as_view(),
        name='attendees_assign_ticket'),
    url(r'^mine/resend/$',
        views.UserResendInvoiceView.as_view(),
        name='attendees_user_resend_invoice'),
)

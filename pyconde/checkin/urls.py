# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, patterns


urlpatterns = patterns(
    'pyconde.checkin.views',
    url('^purchase/$', 'on_desk_purchase_view',
        name='checkin_purchase'),
    url('^purchase/done/$', 'on_desk_purchase_done_view',
        name='checkin_purchase_done'),
    url('^search/$', 'search_view',
        name='checkin_search'),
)

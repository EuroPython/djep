# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns


urlpatterns = patterns('pyconde.attendees.views',
    url(r'^$', 'purchase', name='attendees_purchase'),
    url(r'^names/(?P<pk>\d+)/$', 'purchase_names',
        name='attendees_purchase_names'),
    url(r'^confirm/(?P<pk>\d+)/$', 'purchase_confirm',
        name='attendees_purchase_confirm'),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^done/$', 'direct_to_template',
        {'template': 'attendees/purchase_done.html'},
        name='attendees_purchase_done'),
)

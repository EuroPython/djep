# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, patterns

from . import views


urlpatterns = patterns(
    'pyconde.checkin.views',
    url('^search/$', views.SearchView.as_view(),
        name='checkin_search'),
)

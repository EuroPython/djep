# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin


admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tickets/', include('pyconde.attendees.urls')),
    url(r'^accounts/', include('pyconde.accounts.urls')),
    url(r'^accounts/', include('userprofiles.urls')),
    url(r'^reviews/', include('pyconde.reviews.urls')),
    url(r'^schedule/', include('pyconde.schedule.urls')),
    url(r'^proposals/', include('pyconde.proposals.urls')),
    url(r'^search/', include('pyconde.search.urls')),
    url(r'^', include('cms.urls')),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )

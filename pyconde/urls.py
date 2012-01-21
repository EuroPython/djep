# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()
handler500 = 'pyconde.helpers.views.server_error'


urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('pyconde.accounts.urls')),
    url(r'^accounts/', include('userprofiles.urls')),
    url(r'^', include('cms.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )

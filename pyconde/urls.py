# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    #url(r'^2011/(?P<path>.*)$', 'django.views.generic.simple.redirect_to', {
    #        'permanent': True,
    #        'query_string': True,
    #        'url': 'http://2011.de.pycon.org/2011/%(path)s'}),
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

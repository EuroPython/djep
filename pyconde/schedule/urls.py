from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^session-by-proposal/(?P<proposal_pk>\d+)/$', views.session_by_proposal, name='session_by_proposal'),
    url(r'^sessions/(?P<session_pk>\d+)/$', views.view_session, name='session'),
    url(r'^sessions/tags/(?P<tag>[^/]+)/$', views.sessions_by_tag, name='sessions_by_tag'),
    url(r'^sessions/locations/(?P<pk>[^/]+)/$', views.sessions_by_location, name='sessions_by_location'),
    url(r'^events/(?P<pk>\d+)/$', views.view_session, name='side_event'),
    url(r'^schedule/$', views.view_schedule, name='schedule'),
    )

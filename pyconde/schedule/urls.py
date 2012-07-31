from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^session-by-proposal/(?P<proposal_pk>\d+)/$', views.session_by_proposal, name='session_by_proposal'),
    url(r'^sessions/(?P<session_pk>\d+)/$', views.view_session, name='session'),
    url(r'^schedule/$', views.view_schedule, name='schedule'),
    )

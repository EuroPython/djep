from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    # url(r'^session-by-proposal/(?P<proposal_pk>\d+)/$', views.session_by_proposal, name='session_by_proposal'),
    url(r'^sessions/(?P<session_pk>\d+)/$', views.view_session, name='session'),
    url(r'^sessions/(?P<session_pk>\d+)/attend/$', views.attend_session, {'attending': True}, name='session-attend'),
    url(r'^sessions/(?P<session_pk>\d+)/leave/$', views.attend_session, {'attending': False}, name='session-leave'),
    url(r'^sessions/(?P<session_pk>\d+)/edit/$', views.edit_session, name='edit_session'),
    url(r'^sessions/tags/(?P<tag>.+)/$', views.sessions_by_tag, name='sessions_by_tag'),
    url(r'^sessions/locations/(?P<pk>[^/]+)/$', views.sessions_by_location, name='sessions_by_location'),
    url(r'^sessions/kind/(?P<pk>[^/]+)/$', views.sessions_by_kind, name='sessions_by_kind'),
    url(r'^events/(?P<pk>\d+)/$', views.view_sideevent, name='side_event'),
    url(r'^schedule/$', views.view_schedule, name='schedule'),
    url(r'^attendances/$', views.list_user_attendances, name='schedule-attendances'),
    # url(r'^export/guidebook/sections.csv$', views.guidebook_export_sections, name='guidebook-export-sections'),
    # url(r'^export/guidebook/sessions.csv$', views.guidebook_export_sessions, name='guidebook-export-sessions'),
    # url(r'^export/guidebook/speakers.csv$', views.guidebook_export_speakers, name='guidebook-export-speakers'),
    # url(r'^export/guidebook/speaker-links.csv$', views.guidebook_export_speaker_links, name='guidebook-export-speaker-links'),
    # url(r'^export/guidebook/sponsors.csv$', views.guidebook_export_sponsors, name='guidebook-export-sponsors'),
)

from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^proposal/(?P<pk>\d+)/$', views.ProposalDetailsView.as_view(), name='reviews-proposal-details'),
    url(r'^proposal/(?P<pk>\d+)/comment/$', views.SubmitCommentView.as_view(), name='reviews-submit-comment'),
    url(r'^proposal/(?P<pk>\d+)/update/$', views.UpdateProposalView.as_view(), name='reviews-update-proposal'),
    )

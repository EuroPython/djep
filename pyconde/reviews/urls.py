from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^proposals/$', views.ListProposalsView.as_view(), name='reviews-available-proposals'),
    url(r'^proposals/(?P<pk>\d+)/$', views.ProposalDetailsView.as_view(), name='reviews-proposal-details'),
    url(r'^proposals/(?P<pk>\d+)/comment/$', views.SubmitCommentView.as_view(), name='reviews-submit-comment'),
    url(r'^proposals/(?P<pk>\d+)/update/$', views.UpdateProposalView.as_view(), name='reviews-update-proposal'),
    url(r'^proposals/(?P<pk>\d+)/review/$', views.SubmitReviewView.as_view(), name='reviews-review-proposal'),
    url(r'^proposals/(?P<pk>\d+)/update-review/$', views.UpdateReviewView.as_view(), name='reviews-update-review'),
    url(r'^proposals/(?P<pk>\d+)/delete-review/$', views.DeleteReviewView.as_view(), name='reviews-delete-review'),
    )

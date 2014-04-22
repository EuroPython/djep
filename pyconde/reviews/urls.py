from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^my/$', views.MyReviewsView.as_view(), name='reviews-my-reviews'),
    url(r'^proposals/$', views.ListProposalsView.as_view(), name='reviews-available-proposals'),
    url(r'^proposals/my/$', views.ListMyProposalsView.as_view(), name='reviews-my-proposals'),
    url(r'^proposals/(?P<pk>\d+)/$', views.ProposalDetailsView.as_view(), name='reviews-proposal-details'),
    url(r'^proposals/(?P<pk>\d+)/comment/$', views.SubmitCommentView.as_view(), name='reviews-submit-comment'),
    url(r'^proposals/(?P<proposal_pk>\d+)/comment/(?P<pk>\d+)/delete/$', views.DeleteCommentView.as_view(), name='reviews-delete-comment'),
    url(r'^proposals/(?P<pk>\d+)/update/$', views.UpdateProposalView.as_view(), name='reviews-update-proposal'),
    url(r'^proposals/(?P<pk>\d+)/review/$', views.SubmitReviewView.as_view(), name='reviews-review-proposal'),
    url(r'^proposals/(?P<proposal_pk>\d+)/versions/$', views.ProposalVersionListView.as_view(), name='reviews-versions'),
    url(r'^proposals/(?P<proposal_pk>\d+)/versions/(?P<pk>\d+)/$', views.ProposalVersionDetailsView.as_view(), name='reviews-version-details'),
    url(r'^proposals/(?P<pk>\d+)/update-review/$', views.UpdateReviewView.as_view(), name='reviews-update-review'),
    url(r'^proposals/(?P<pk>\d+)/delete-review/$', views.DeleteReviewView.as_view(), name='reviews-delete-review'),
    url(r'^proposals/(?P<proposal_pk>\d+)/reviews/$', views.ProposalReviewsView.as_view(), name='reviews-proposal-reviews'),
)

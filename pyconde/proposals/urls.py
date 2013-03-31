from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views
from . import settings


urlpatterns = patterns(
    '',
    url(r'^/?$', views.IndexView.as_view(),
        name='proposals_index'),
    url(r"^view/(?P<pk>\d+)/",
        views.SingleProposalView.as_view(),
        name="view_proposal"),
    url(r'^submit/$',
        views.SubmitProposalView.as_view(),
        name='submit_proposal'),
    url(r"^edit/(?P<pk>\d+)/",
        views.EditProposalView.as_view(),
        name="edit_proposal"),
    url(r"^cancel/(?P<pk>\d+)/",
        views.CancelProposalView.as_view(),
        name="cancel_proposal"),
    url(r"^leave/(?P<pk>\d+)/",
        views.LeaveProposalView.as_view(),
        name="leave_proposal"),
    url(r"^mine/$",
        views.ListUserProposalsView.as_view(),
        name="my_proposals"),
)

if not settings.UNIFIED_SUBMISSION_FORM:
    urlpatterns += patterns(
        '',
        url(r'^submit/(?P<type>\S+)/$',
            views.SubmitProposalView.as_view(),
            name='typed_submit_proposal'),
    )

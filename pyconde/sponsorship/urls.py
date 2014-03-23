from django.conf.urls import url, patterns

from pyconde.sponsorship import views


urlpatterns = patterns('',
    url(r'^send_job_offer/$',
        views.JobOffer.as_view(),
        name='sponsorship_send_job_offer')
)

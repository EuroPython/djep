from django.conf.urls import url, patterns


urlpatterns = patterns('pyconde.sponsorship.views',
    url(r'^$',
        'list_sponsors',
        name='sponsorship_list'),
    url(r'^send_job_offer/$',
        'job_offer',
        name='sponsorship_send_job_offer')
)

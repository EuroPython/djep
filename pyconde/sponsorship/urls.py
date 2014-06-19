from django.conf.urls import url, patterns


urlpatterns = patterns('pyconde.sponsorship.views',
    url(r'^$',
        'list_sponsors',
        name='sponsorship_list'),
    url(r'^job_offers/$',
        'job_offers_list_view',
        name='sponsorship_job_offers'),
    url(r'^send_job_offer/$',
        'send_job_offer_view',
        name='sponsorship_send_job_offer')
)

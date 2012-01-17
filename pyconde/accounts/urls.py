from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('accounts.views',
    url(r'^$', 'profile_change', name='accounts_profile_change'),
    url(r'^email/$', 'email_change', name='accounts_email_change'),
    url(r'^email/requested/$', 'email_change_requested',
        name='accounts_email_change_requested'),
    url(r'^email/confirm/(?P<token>[0-9A-Za-z-]+)/(?P<code>[0-9A-Za-z-]+)/$',
        'email_change_approve', name='accounts_email_change_approve'),
)

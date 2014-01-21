from django.conf.urls import patterns, url

from .feed import LatestNewsItemsFeed


urlpatterns = patterns('',
    url(r'^feed/$', LatestNewsItemsFeed(), name='news-feed'),
)

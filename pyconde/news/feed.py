# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from cms.utils.page_resolver import get_page_queryset

from pyconde.conference.models import current_conference

from .models import NewsItemPlugin


class LatestNewsItemsFeed(Feed):
    feed_type = Atom1Feed

    title = current_conference().title
    link = "/news/"
    description = _("Latest news from %(conference_title)s") % {'conference_title': title}

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(LatestNewsItemsFeed, self).__call__(request, *args, **kwargs)

    def items(self):
        page = get_page_queryset(self.request).get(reverse_id='news')
        return NewsItemPlugin.objects.filter(placeholder__page=page) \
                                     .order_by('-publish_date')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link or item.get_absolute_url() or self.link

    def item_pubdate(self, item):
        return item.publish_date

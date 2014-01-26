# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models


class CMSNewsItemPlugin(CMSPluginBase):
    model = models.NewsItemPlugin
    name = _('News item')
    render_template = "news/plugins/news_item.html"


class CMSNewsCollectionPlugin(CMSPluginBase):
    model = models.NewsCollectionPlugin
    name = _('News collection')
    render_template = "news/plugins/news_collection.html"
    allow_children = True


plugin_pool.register_plugin(CMSNewsItemPlugin)
plugin_pool.register_plugin(CMSNewsCollectionPlugin)

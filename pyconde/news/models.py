# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


class NewsItemPlugin(CMSPlugin):
    """
    Holds a news entry
    """
    title = models.CharField(_('Title'), max_length=255)
    publish_date = models.DateTimeField(_('Published on'), auto_now_add=True)

    class Meta:
        ordering = ('-publish_date',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.placeholder and self.placeholder.page:
            return self.placeholder.page.get_absolute_url() + "#" + self.url_target
        return None

    @property
    def url_target(self):
        if self.pk:
            return "n%d" % self.pk
        return ""


class NewsCollectionPlugin(CMSPlugin):
    """
    Container for testimonials that is rendered as as slider.
    """
    pass

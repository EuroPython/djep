# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin, Page


class NewsItemPlugin(CMSPlugin):
    """
    Holds a news entry
    """
    title = models.CharField(_('Title'), max_length=255)
    publish_date = models.DateTimeField(_('Published on'), auto_now_add=True)
    description = models.TextField(_('Text'), blank=True, default="",
        help_text=_('This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" rel="external">Markdown</a> input.'))

    # From cms.plugins.link
    url = models.URLField(_("link"), blank=True, null=True)
    page_link = models.ForeignKey(Page, verbose_name=_("page"), blank=True,
        null=True, help_text=_("A link to a page has priority over a text link."))

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

    # From cms.plugins.link
    @property
    def link(self):
        """
        Returns the link with highest priority among the model fields
        """
        if self.url:
            return self.url
        elif self.page_link:
            return self.page_link.get_absolute_url()
        else:
            return None


class NewsCollectionPlugin(CMSPlugin):
    """
    Container for testimonials that is rendered as as slider.
    """
    pass

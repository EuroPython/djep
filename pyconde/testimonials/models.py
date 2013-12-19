from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


class TestimonialPlugin(CMSPlugin):
    """
    Lists all testimonials currently active.
    """
    content = models.TextField(_("content"))
    author = models.CharField(_("author"), max_length=255)
    author_image = models.ImageField(_("author's photo"),
        upload_to='testimonials')
    author_url = models.URLField(_("author's website"), null=True, blank=True)
    author_description = models.CharField(_("author's description"),
        max_length=100, blank=True)


class TestimonialCollectionPlugin(CMSPlugin):
    pass

from django.db import models
from django.utils.translation import ugettext_lazy as _

from sortedm2m.fields import SortedManyToManyField


class LightningTalk(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    speakers = SortedManyToManyField(
        "speakers.Speaker", related_name='lightning_talks', null=True,
        blank=True, verbose_name=_("speakers"))
    description = models.TextField(_("description"), blank=True, null=True)
    slides_url = models.URLField(_("slides URL"), blank=True, null=True)

    def __unicode__(self):
        return self.title
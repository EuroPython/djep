from django.db import models
from django.utils.translation import ugettext_lazy as _

from pyconde.conference.models import Conference, CurrentConferenceManager


class Event(models.Model):
    conference = models.ForeignKey(Conference, verbose_name=_("Conference"))
    title = models.CharField(_("Title"), max_length=255)
    date = models.DateTimeField(_("Date"))
    link = models.URLField(_("Link"), blank=True, null=True,
        verify_exists=False)

    objects = CurrentConferenceManager()

    class Meta(object):
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['date']

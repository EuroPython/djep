from django.db import models
from django.utils.translation import ugettext_lazy as _

from pyconde.conference.models import Conference, CurrentConferenceManager


class Event(models.Model):
    conference = models.ForeignKey(Conference, verbose_name=_("Conference"))
    title = models.CharField(_("Title"), max_length=255)
    date = models.DateTimeField(_("Date"))
    end_date = models.DateTimeField(_("End date"), blank=True, null=True)
    link = models.URLField(_("Link"), blank=True, null=True)

    objects = models.Manager()
    current_conference = CurrentConferenceManager()

    class Meta(object):
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['date']

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.markup.templatetags.markup import markdown
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django import forms

from pyconde.conference.models import CurrentConferenceManager, current_conference
from pyconde.tagging import TaggableManager


DATE_SLOT_CHOICES = (
    (1, _('morning')),
    (2, _('afternoon')),
)

LANGUAGES_CHOICES = [(x[0], _(x[1])) for x in getattr(settings, 'PROPOSAL_LANGUAGES', (
    ('de', _('German')),
    ('en', _('English')),
))]


class TimeSlot(models.Model):
    """
    A timeslot is used by the proposal model to represent possible times
    the speaker can do his/her talk. We just split this up into morning
    and afternoon.
    """
    date = models.DateField(_("date"))
    slot = models.IntegerField(_("timeslot"), choices=DATE_SLOT_CHOICES)
    section = models.ForeignKey('conference.Section', verbose_name=_("section"))

    def __unicode__(self):
        return "{0}, {1}".format(
            self.date, dict(DATE_SLOT_CHOICES)[self.slot])

    class Meta(object):
        ordering = ('date',)
        unique_together = (('date', 'slot', 'section',),)
        verbose_name = _("timeslot")
        verbose_name_plural = _("timeslots")


class AbstractProposal(models.Model):
    """
    A proposal represents a possible future session as it will be used before
    and during the review process. It has one mandatory speaker and possible
    additional speakers as well as a certain kind (training, session, ...),
    target-audience and proposed duration.
    """
    conference = models.ForeignKey("conference.Conference",
        verbose_name="conference", on_delete=models.PROTECT)
    title = models.CharField(_("title"), max_length=100)
    description = models.TextField(_("description"), max_length=400)
    abstract = models.TextField(_("abstract"))
    notes = models.TextField(_("notes"), blank=True)
    speaker = models.ForeignKey("speakers.Speaker", related_name="%(class)ss",
        verbose_name=_("speaker"), on_delete=models.PROTECT)
    additional_speakers = models.ManyToManyField("speakers.Speaker",
        blank=True, null=True, related_name="%(class)s_participations",
        verbose_name=_("additional speakers"))
    submission_date = models.DateTimeField(_("submission date"), editable=False,
        default=now)
    modified_date = models.DateTimeField(_("modification date"), blank=True,
        null=True)
    kind = models.ForeignKey("conference.SessionKind", verbose_name=_("type"),
        on_delete=models.PROTECT)
    audience_level = models.ForeignKey("conference.AudienceLevel",
        verbose_name=_("target-audience"), on_delete=models.PROTECT)
    duration = models.ForeignKey("conference.SessionDuration",
        verbose_name=_("duration"), on_delete=models.PROTECT)
    track = models.ForeignKey("conference.Track", verbose_name=_("track"),
        blank=True, null=True, on_delete=models.PROTECT)
    available_timeslots = models.ManyToManyField(TimeSlot,
        verbose_name=_("available timeslots"), null=True, blank=True)
    language = models.CharField(_('language'), max_length=5, blank=False,
        default=LANGUAGES_CHOICES[0][0], choices=LANGUAGES_CHOICES)
    accept_recording = models.BooleanField(default=True, blank=True)
    tags = TaggableManager(blank=True)

    objects = models.Manager()
    current_conference = CurrentConferenceManager()

    class Meta(object):
        abstract = True

    def clean(self):
        super(AbstractProposal, self).clean()
        try:
            if self.conference is not None and self.duration.conference != self.conference:
                raise forms.ValidationError(_("The duration has to be associated with the same conference as the proposal"))
        except:
            pass

    def get_absolute_url(self):
        return reverse("view_proposal", kwargs=dict(pk=self.pk))

    def __unicode__(self):
        try:
            return "{0} ({1})".format(self.title, self.conference)
        except:
            return self.title

    @cached_property
    def abstract_rendered(self):
        return markdown(self.abstract, 'safe')

    @cached_property
    def description_rendered(self):
        return markdown(self.description, 'safe')


class Proposal(AbstractProposal):
    class Meta(object):
        verbose_name = _("proposal")
        verbose_name_plural = _("proposals")
        ordering = ['-pk']
        permissions = (
            ("see_proposal_author", _("Can always see the proposal author")),
        )

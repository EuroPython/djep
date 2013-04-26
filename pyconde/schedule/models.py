import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import django.db.models.signals as model_signals
from django.core.cache import cache

from cms.models import CMSPlugin


from ..proposals import models as proposal_models
from ..reviews import models as review_models
from ..conference import models as conference_models


LOG = logging.getLogger(__name__)


class Session(proposal_models.AbstractProposal):
    """
    The session is the final step on the way that started with the initial
    session proposal. Because of that it also shares the same fields with
    the original proposal data structure but ammends that with fields for
    representing the time and place where and when the session is actually
    taking place.
    """
    start = models.DateTimeField(_("start time"), blank=True, null=True)
    end = models.DateTimeField(_("end time"), blank=True, null=True)
    section = models.ForeignKey(conference_models.Section, blank=True,
        null=True, verbose_name=_("section"), related_name='sessions')
    proposal = models.ForeignKey(proposal_models.Proposal,
        blank=True, null=True,
        related_name='session',
        verbose_name=_("proposal"))
    location = models.ForeignKey(conference_models.Location,
        verbose_name=_("location"), blank=True, null=True)
    is_global = models.BooleanField(_("is global"), default=False)
    released = models.BooleanField(_("released"), default=False)
    slides_url = models.URLField(_("Slides URL"), blank=True, null=True)
    video_url = models.URLField(_("Video URL"), blank=True, null=True)

    @classmethod
    def create_from_proposal(cls, proposal):
        """
        Creates an saved instance of a session based on the data available
        in a given proposal.
        """
        obj = cls()
        obj.load_from_proposal(proposal)
        return obj

    def load_from_proposal(self, proposal):
        """
        Copies data from a proposal object and a possibly existing proposal
        version into the current object.
        """
        assert isinstance(proposal, proposal_models.AbstractProposal)
        LOG.debug("Importing proposal data into session")
        for field in proposal._meta.fields:
            if field.primary_key:
                continue
            setattr(self, field.name, getattr(proposal, field.name))
        self.proposal = proposal
        self.save()
        self.tags.add(*[t.name for t in proposal.tags.all()])
        self.additional_speakers = proposal.additional_speakers.all()

        # Also check if there was an update to that proposal and update the
        # provided values if necessary.
        pv = review_models.ProposalVersion.objects.get_latest_for(proposal)
        if pv:
            LOG.debug("Applying proposal version data")
            for field in proposal._meta.fields:
                if field.primary_key:
                    continue
                setattr(self, field.name, getattr(pv, field.name))
            self.tags.add(*[t.name for t in pv.tags.all()])
            self.additional_speakers = pv.additional_speakers.all()
        self.save()

    def get_absolute_url(self):
        return reverse('session', kwargs={'session_pk': self.pk})

    class Meta(object):
        verbose_name = _('session')
        verbose_name_plural = _('sessions')


class SideEvent(models.Model):
    """
    Side events are either social events or things like breaks and info events
    that take place during the conference days but are not sessions.
    """
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    start = models.DateTimeField(_("start time"))
    end = models.DateTimeField(_("end time"))
    section = models.ForeignKey(conference_models.Section, blank=True,
        null=True, verbose_name=_("section"), related_name='side_events')
    location = models.ForeignKey(conference_models.Location, blank=True,
        null=True, verbose_name=_("location"))
    is_global = models.BooleanField(_("is global"), default=False)
    is_pause = models.BooleanField(_("is pause"), default=False)
    is_recordable = models.BooleanField(_("is recordable"), default=False)
    conference = models.ForeignKey(conference_models.Conference,
        verbose_name=_("conference"))

    objects = models.Manager()
    current_conference = conference_models.CurrentConferenceManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('side_event', kwargs={'pk': self.pk})


class CompleteSchedulePlugin(CMSPlugin):
    """
    Renders the complete schedule for the active conference.
    """
    sections = models.ManyToManyField(conference_models.Section,
        blank=True, null=True, verbose_name=_("sections"))


def clear_schedule_caches(sender, *args, **kwargs):
    instance = kwargs.get('instance', None)
    if not instance:
        return
    # We have to clear the cache for every section of the current conference as
    # well as the global cache itself.
    conf = conference_models.current_conference()
    cache_keys = [
        'schedule:{0}:30'.format(conf.pk),
        'schedule:guidebook:events'
    ]
    for section in conf.sections.all():
        cache_keys.append('section_schedule:{0}:30'.format(section.pk))
    LOG.debug("Clearing following cache keys: " + unicode(cache_keys))
    cache.delete_many(cache_keys)

model_signals.post_save.connect(clear_schedule_caches, sender=SideEvent)
model_signals.post_save.connect(clear_schedule_caches, sender=Session)
model_signals.post_delete.connect(clear_schedule_caches, sender=SideEvent)
model_signals.post_delete.connect(clear_schedule_caches, sender=Session)

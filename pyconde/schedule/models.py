import logging

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, signals as model_signals
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from cms.models import CMSPlugin

from ..proposals import models as proposal_models
from ..reviews import models as review_models
from ..conference import models as conference_models


LOG = logging.getLogger(__name__)


EVENT_ICON_CHOICES = (
    ('coffee', _('Coffee cup')),
    ('glass', _('Glass')),
    ('lightbulb-o', _('Lightbulb')),
    ('moon-o', _('Moon')),
    ('cutlery', _('Cutlery')),
)


class AttendingError(Exception):
    pass


class LocationMixin(object):

    def location_pretty(self):
        pretty = getattr(self, '_location_pretty', None)
        if pretty is None:
            pretty = ', '.join(map(force_text, self.location.all()))
            setattr(self, '_location_pretty', pretty)
        return pretty
    location_pretty.short_description = _('Locations')

    location_pretty = property(location_pretty)


class Session(LocationMixin, proposal_models.AbstractProposal):
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
    proposal = models.ForeignKey(proposal_models.Proposal, blank=True,
        null=True, related_name='session', verbose_name=_("proposal"))
    location = models.ManyToManyField(conference_models.Location,
        verbose_name=_("location"), blank=True, null=True)
    is_global = models.BooleanField(_("is global"), default=False)
    released = models.BooleanField(_("released"), default=False)
    slides_url = models.URLField(_("Slides URL"), blank=True, null=True)
    video_url = models.URLField(_("Video URL"), blank=True, null=True)

    max_attendees = models.PositiveSmallIntegerField(_('Max attendees'),
        null=True, blank=True)

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
        self.available_timeslots = proposal.available_timeslots.all()

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

    def can_attend(self, user):
        other = Session.objects.filter(attendees=user.profile).exclude(id=self.pk)
        q_overlap = (
            Q(start__range=(self.start, self.end)) |
            Q(end__range=(self.start, self.end))
        )
        other = other.filter(q_overlap)
        return not other.exists()

    def is_attending(self, user):
        if user.pk:
            return self.attendees.filter(id=user.profile.id).exists()
        return False

    def attend(self, user):
        current_time = now()
        if self.start <= current_time:
            if self.end <= current_time:
                raise AttendingError(_('You cannot attend this session anymore. The session already ended.'))
            else:
                raise AttendingError(_('You cannot attend this session anymore. The session already started.'))
        elif not self.has_free_seats():
            raise AttendingError(_('You cannot attend right no. No empty seats.'))
        elif not self.can_attend(user):
            raise AttendingError(_('You cannot attend this session. Already attending another session at that time.'))
        else:
            self.attendees.add(user.profile.id)

    def unattend(self, user):
        current_time = now()
        if self.start <= current_time:
            if self.end <= current_time:
                raise AttendingError(_('You cannot leave this session anymore. The session already ended.'))
            else:
                raise AttendingError(_('You cannot leave this session anymore. The session already started.'))
        else:
            self.attendees.remove(user.profile.id)

    def has_free_seats(self):
        if self.max_attendees in (None, 0):
            return True
        return self.attendees.count() < self.max_attendees

    class Meta(object):
        verbose_name = _('session')
        verbose_name_plural = _('sessions')


class SideEvent(LocationMixin, models.Model):
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
    location = models.ManyToManyField(conference_models.Location, blank=True,
        null=True, verbose_name=_("location"))
    is_global = models.BooleanField(_("is global"), default=False)
    is_pause = models.BooleanField(_("is break"), default=False)
    is_recordable = models.BooleanField(_("is recordable"), default=False)
    conference = models.ForeignKey(conference_models.Conference,
        verbose_name=_("conference"))
    icon = models.CharField(max_length=50, blank=True, null=True,
        verbose_name=_("icon"), choices=EVENT_ICON_CHOICES)

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

    ROW_DURATION_15 = 15
    ROW_DURATION_30 = 30
    ROW_DURATION_45 = 45
    ROW_DURATION_60 = 60
    ROW_DURATION_CHOICES = (
        (ROW_DURATION_15, _('15 Minutes')),
        (ROW_DURATION_30, _('30 Minutes')),
        (ROW_DURATION_45, _('45 Minutes')),
        (ROW_DURATION_60, _('60 Minutes')),
    )

    title = models.CharField(max_length=100, blank=True,
        verbose_name=_('title'))
    sections = models.ManyToManyField(conference_models.Section,
        blank=True, null=True, verbose_name=_("sections"))
    row_duration = models.IntegerField(_('Duration of one row'),
        choices=ROW_DURATION_CHOICES, default=ROW_DURATION_15)
    merge_sections = models.BooleanField(_('Merge different section into same table'),
        default=False)


def clear_schedule_caches(sender, *args, **kwargs):
    from itertools import product
    # We have to clear the cache for every section of the current conference as
    # well as the global cache itself.
    conf = conference_models.current_conference()
    cache_keys = [
        'schedule:guidebook:events'
    ]
    section_ids = list(conf.sections.values_list('id', flat=True)) + ['__merged__']
    durations = dict(CompleteSchedulePlugin.ROW_DURATION_CHOICES).keys()
    prod = product(section_ids, durations)
    for sec, dur in prod:
        cache_keys.append('schedule:{0}:{1}'.format(conf.pk, dur))
        cache_keys.append('section_schedule:{0}:{1}'.format(sec, dur))
    LOG.debug("Clearing following cache keys: " + unicode(cache_keys))
    cache.delete_many(cache_keys)

model_signals.post_save.connect(clear_schedule_caches, sender=SideEvent)
model_signals.post_save.connect(clear_schedule_caches, sender=Session)
model_signals.post_delete.connect(clear_schedule_caches, sender=SideEvent)
model_signals.post_delete.connect(clear_schedule_caches, sender=Session)

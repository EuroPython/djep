import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

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
        null=True, verbose_name=u"section", related_name='sessions')
    proposal = models.ForeignKey(proposal_models.Proposal,
        blank=True, null=True,
        related_name='session',
        verbose_name=_("proposal"))
    location = models.ForeignKey(conference_models.Location,
        verbose_name=_("location"), blank=True, null=True)

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
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    section = models.ForeignKey(conference_models.Section, blank=True,
        null=True, verbose_name=u"section", related_name='side_events')
    location = models.ForeignKey(conference_models.Location, blank=True,
        null=True)
    is_global = models.BooleanField(default=False)
    conference = models.ForeignKey(conference_models.Conference,
        verbose_name=_("conference"))

    objects = conference_models.CurrentConferenceManager()

    def __unicode__(self):
        return self.name

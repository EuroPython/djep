from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..proposals import models as proposal_models
from ..reviews import models as review_models
from ..conference import models as conference_models


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
    proposal = models.ForeignKey(proposal_models.Proposal,
        related_name='session',
        verbose_name=_("proposal"))
    location = models.ForeignKey(conference_models.Location,
        verbose_name=_("location"), blank=True, null=True)

    @classmethod
    def init_from_proposal(cls, proposal):
        """
        Creates an unsaved instance of a session based on the data available
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
        for field in proposal._meta.fields:
            if field.primary_key:
                continue
            setattr(self, field.name, getattr(proposal, field.name))
        self.tags = proposal.tags
        self.proposal = proposal

        # Also check if there was an update to that proposal and update the
        # provided values if necessary.
        pv = review_models.ProposalVersion.objects.get_latest_for(proposal)
        if pv:
            for field in proposal._meta.fields:
                if field.primary_key:
                    continue
                setattr(self, field.name, getattr(pv, field.name))
            self.tags = pv.tags

    class Meta(object):
        verbose_name = _('session')
        verbose_name_plural = _('sessions')

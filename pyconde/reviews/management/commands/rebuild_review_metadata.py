from django.core.management.base import BaseCommand

from ... import models
from pyconde.proposals import models as proposal_models

class Command(BaseCommand):
    help = """Rebuilds metadata of proposals."""

    def handle(self, *args, **kwargs):
        for proposal in proposal_models.Proposal.objects.all():
            models._update_proposal_metadata(proposal)

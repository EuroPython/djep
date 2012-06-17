from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = """Rebuilds metadata of proposals."""

    def handle(self, *args, **kwargs):
        for proposal in models.Proposal.objects.all():
            models._update_proposal_metadata(proposal)

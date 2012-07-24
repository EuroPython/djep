from django.core.management.base import BaseCommand

from ... import utils


class Command(BaseCommand):
    help = """Exports proposals with their scores"""

    def handle(self, *args, **kwargs):
        print utils.create_proposal_score_export().csv

from django.core.management.base import BaseCommand

from ... import exporters
from ... import models


class Command(BaseCommand):
    help = """Exports proposals with their scores"""

    def handle(self, *args, **kwargs):
        print exporters.SimpleSessionExporter(models.Session.objects.all())().csv

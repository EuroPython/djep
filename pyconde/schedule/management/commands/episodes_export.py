from django.core.management.base import BaseCommand
import json

from ... import exporters


class Command(BaseCommand):
    help = """
    Exports all sessions for the video team
    """

    def handle(self, *args, **kwargs):
        exporter = exporters.SessionForEpisodesExporter()
        print json.dumps(exporter(), indent=4)

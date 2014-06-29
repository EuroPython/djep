# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ... import exporters


class Command(BaseCommand):
    help = """
    Exports all sessions and side-events as CSV for guidebook.

    Following columns are included:

    * title
    * date
    * start time
    * end time
    * location name
    * track name
    * description
    """

    def handle(self, *args, **kwargs):
        exporter = exporters.GuidebookExporterSpeakerLinks()
        self.stdout.write(exporter().csv)

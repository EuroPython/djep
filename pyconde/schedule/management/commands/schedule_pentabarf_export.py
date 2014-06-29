# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ... import exporters


class Command(BaseCommand):
    help = """
    Exports all sessions as pentabarf xcalendar
    """

    def handle(self, *args, **kwargs):
        exporter = exporters.XMLExporterPentabarf()
        self.stdout.write(exporter.export().getvalue())

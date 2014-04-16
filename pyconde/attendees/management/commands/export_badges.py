# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from pyconde.attendees.exporters import BadgeExporter
from pyconde.attendees.models import VenueTicket


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--base-url',
            action='store_true',
            dest='base_url',
            default='',
            help='Base URL for profile URLs'),
        make_option('--indent',
            action='store_true',
            dest='indent',
            default=None,
            help='Base URL for profile URLs'),
        )

    help = 'Export all valid venue / conference tickets'

    def handle(self, *args, **options):
        qs = VenueTicket.objects.filter(purchase__state='payment_received')
        exporter = BadgeExporter(qs, base_url=options['base_url'],
            indent=options['indent'])
        self.stdout.write(exporter.json)

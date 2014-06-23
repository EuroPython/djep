# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from pyconde.attendees.exporters import BadgeExporter
from pyconde.attendees.models import VenueTicket


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--base-url',
            action='store',
            dest='base_url',
            default='',
            help='Base URL for profile URLs. Use {uid} as placeholder to '
                 'circumvent URL resolving and use custom URLs'),
        make_option('--indent',
            action='store_true',
            dest='indent',
            default=None,
            help='Indent the output'),
        make_option('--exclude-ticket-type',
            action='store',
            dest='exclude_tt',
            default=None,
            help='comma separated list of ticket type IDs to exclude'),
        )

    help = 'Export all valid venue / conference tickets'

    def handle(self, *args, **options):
        qs = VenueTicket.objects.only_valid()
        if options['exclude_tt'] is not None:
            excluded_tt_ids = map(int, options['exclude_tt'].split(','))
            qs = qs.exclude(ticket_type_id__in=excluded_tt_ids)
        exporter = BadgeExporter(qs, base_url=options['base_url'],
            indent=options['indent'])
        self.stdout.write(exporter.json)

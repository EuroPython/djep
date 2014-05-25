# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from ...exporters import XMLExporter


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--out', '-o',
            action='store',
            dest='outfile',
            default='',
            help='Output file'),
        make_option('--base-url',
            action='store',
            dest='base_url',
            default='',
            help='Base URL for profile URLs'),
        make_option('--pretty',
            action='store_true',
            dest='pretty',
            default=False,
            help='Create pretty XML'),
        make_option('--export-avatars',
            action='store_true',
            dest='export_avatars',
            default=False,
            help='Copy avatars of speakers into separate directory'),
        )

    help = 'Export all valid venue / conference tickets'

    def handle(self, *args, **options):
        if not options['outfile']:
            raise CommandError('expected an output file')
        if not options['outfile'].endswith('.xml'):
            options['outfile'] += '.xml'
        exporter = XMLExporter(options['outfile'], base_url=options['base_url'],
                               pretty=options['pretty'], export_avatars=options['export_avatars'])
        exporter.export()

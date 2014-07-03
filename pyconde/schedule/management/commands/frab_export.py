import codecs

from optparse import make_option

from django.core.management.base import BaseCommand

from ... import exporters


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--out', '-o',
            action='store',
            dest='outfile',
            default=None,
            help='Output file'),
        )

    def handle(self, *args, **kwargs):
        output_file = kwargs.get('outfile')
        if output_file:
            with codecs.open(output_file, 'w+', encoding='utf-8') as fp:
                exporters.FrabExporter(fp)()
        else:
            exporters.FrabExporter()()

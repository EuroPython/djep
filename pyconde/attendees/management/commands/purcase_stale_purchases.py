from __future__ import print_function
import datetime

from django.core.management.base import BaseCommand, make_option

from ... import models


class Command(BaseCommand):
    help = 'This removes orders with the status "incomplete" that have been'
    ' created more than n days ago.'

    option_list = BaseCommand.option_list + (
        make_option('-d', '--days', action='store', dest='days', default=7,
                    type='int',
                    help='Number of days prior to which purchases should be purged'),
    )

    def handle(self, *args, **options):
        print("Purging orders older than {0} day(s):".format(options['days']))
        date = datetime.datetime.now() - datetime.timedelta(days=options['days'])
        for purchase in models.Purchase.objects.filter(state='incomplete', date_added__lt=date):
            print(purchase, purchase.date_added)
            purchase.delete()

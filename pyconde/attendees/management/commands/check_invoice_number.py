from __future__ import print_function
import sys

from django.core.management.base import BaseCommand
from django.db.models import Max

from redis_cache import get_redis_connection

from pyconde.conference.models import current_conference

from ... import models
from ... import settings


class Command(BaseCommand):
    help = "Checks that no invoice number is newer than what is stored in Redis."

    def handle(self, *args, **options):
        max_in_db = models.Purchase.objects\
            .filter(conference=current_conference())\
            .aggregate(Max('invoice_number'))\
            .get('invoice_number__max', 0)
        redis = get_redis_connection()
        redis_value = redis.get(settings.INVOICE_NUMBER_SEQUENCE_NAME)
        if redis_value is None:
            redis_value = 0
        else:
            redis_value = int(redis_value)
        if redis_value != max_in_db:
            print("Sequence stored in Redis is different from latest invoice in database: {0} vs. {1}".format(
                redis_value, max_in_db), file=sys.stderr)
            sys.exit(1)
        else:
            print("OK")

import tablib

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from ... import models, utils

class Command(BaseCommand):
    help = _("Exports all reviews as CSV to stdout")
    def handle(self, *args, **kwargs):
        qs = models.Review.objects.select_related('proposal', 'user').all()
        print utils.create_reviews_export(qs).csv

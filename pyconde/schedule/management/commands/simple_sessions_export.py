from django.core.management.base import BaseCommand

from ... import utils
from ... import models


class Command(BaseCommand):
    help = """Exports proposals with their scores"""

    def handle(self, *args, **kwargs):
        print utils.create_simple_export(models.Session.objects.all()).csv

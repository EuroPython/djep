# see https://github.com/divio/django-cms/issues/1031

from django.core.management.commands import loaddata
from django.db.models import signals
from cms.signals import update_placeholders
from cms.models import Page

class Command(loaddata.Command):

    def handle(self, *fixture_labels, **options):
        signals.post_save.disconnect(update_placeholders, sender=Page)

        loaddata.Command.handle(self, *fixture_labels, **options)

        signals.post_save.connect(update_placeholders, sender=Page)

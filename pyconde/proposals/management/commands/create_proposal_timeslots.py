import logging

from django.core.management.base import BaseCommand

from pyconde.conference import models as conference_models

from ... import models
from ... import utils


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    This command creates timeslots for every section of the active conference
    if they don't exist yet. It will also print out a warning if there are
    timeslots available that shouldn't be there.
    """

    def handle(self, *args, **options):
        necessary_slots = set()
        all_slots = set()
        created_slots = set()
        for section in conference_models.Section.current_objects.all():
            if section.start_date and section.end_date:
                for date in utils.get_date_range(section.start_date, section.end_date):
                    for slot in models.DATE_SLOT_CHOICES:
                        obj, created = models.TimeSlot.objects.get_or_create(
                            date=date, slot=slot[0], section=section)
                        necessary_slots.add(obj)
                        if created:
                            LOG.info("Created {0}".format(obj))
                            created_slots.add(obj)
            else:
                LOG.warn("Section {0} has no valid date range!".format(
                    section))
        all_slots.update(list(models.TimeSlot.objects.filter(section__conference=conference_models.current_conference())))

        print("Created {0} slots".format(len(created_slots)))
        unnecessary_slots = all_slots - necessary_slots
        if unnecessary_slots:
            print("Found unnecssary slots:")
            for slot in unnecessary_slots:
                print(" - {0}".format(slot))

import datetime

from django.test import TestCase

from pyconde.conference.test_utils import ConferenceTestingMixin

from . import models
from .templatetags import event_tags


class TaglibTests(ConferenceTestingMixin, TestCase):
    def setUp(self):
        self.create_test_conference()
        self.create_test_conference('other_')

    def tearDown(self):
        self.destroy_all_test_conferences()

    def test_only_current_conference(self):
        """
        This taglib should only list events associated with the current
        conference.
        """
        previous_event = models.Event(
            title="Previous event",
            date=datetime.datetime.now(),
            conference=self.other_conference)
        previous_event.save()
        event = models.Event(
            title="Current event",
            date=datetime.datetime.now(),
            conference=self.conference)
        event.save()
        with self.settings(CONFERENCE_ID=self.conference.pk):
            self.assertEqual([event], list(event_tags.list_events()['events']))

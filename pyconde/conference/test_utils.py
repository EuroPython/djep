from __future__ import unicode_literals

import copy

from . import models as conference_models


class ConferenceTestingMixin(object):
    """
    This is a simple mixin that provides helper methods for initializing
    fully setup conference objects and related models like SessionKinds.
    """
    _registered_conference_setups = set()

    def create_test_conference(self, prefix=None):
        """
        Creates testcase local conference, session kind, track, ... variables
        with the given prefix.
        """
        if prefix in self._registered_conference_setups:
            raise RuntimeError(u"Conference with prefix {0} already set up!"
                               .format(prefix))

        if prefix is None:
            prefix = u""

        conference = conference_models.Conference(title="TestCon")
        conference.save()

        audience_level = conference_models.AudienceLevel(
            level=1,
            name='Level 1', conference=conference
        )
        audience_level.save()

        kind = conference_models.SessionKind(
            conference=conference,
            closed=False, slug='kind'
        )
        kind.save()

        duration = conference_models.SessionDuration(
            minutes=30,
            conference=conference)
        duration.save()

        track = conference_models.Track(
            name="NAME", slug="SLUG",
            conference=conference
        )
        track.save()
        setattr(self, "{0}conference".format(prefix), conference)
        setattr(self, "{0}audience_level".format(prefix), audience_level)
        setattr(self, "{0}kind".format(prefix), kind)
        setattr(self, "{0}duration".format(prefix), duration)
        setattr(self, "{0}track".format(prefix), track)
        self._registered_conference_setups.add(prefix)

    def destroy_test_conference(self, prefix):
        """
        Removes the conference set with the given prefix from the current
        testcase instance.
        """
        if prefix not in self._registered_conference_setups:
            raise RuntimeError("Conference with prefix {0} doesn't exist!"
                               .format(prefix))
        conference = getattr(self, "{0}conference".format(prefix))
        if hasattr(conference, 'proposal_set'):
            conference.proposal_set.all().delete()
        conference.delete()
        getattr(self, "{0}audience_level".format(prefix)).delete()
        getattr(self, "{0}kind".format(prefix)).delete()
        getattr(self, "{0}duration".format(prefix)).delete()
        getattr(self, "{0}track".format(prefix)).delete()
        self._registered_conference_setups.remove(prefix)

    def destroy_all_test_conferences(self):
        """
        Removes all known conference sets from the current testcase instance.
        """
        for prefix in copy.copy(self._registered_conference_setups):
            self.destroy_test_conference(prefix)

from django.core.management.base import BaseCommand

from . import models
import tablib


class SimpleSessionExporter(object):
    def __init__(self, queryset):
        self.queryset = queryset

    def _format_cospeaker(self, s):
        """
        Format the speaker's name for secondary speaker export and removes
        our separator characters to avoid confusion.
        """
        return unicode(s).replace("|", " ")

    def __call__(self):
        queryset = self.queryset.select_related('duration', 'track', 'proposal',
            'speaker', 'latest_proposalversion__track', 'audience_level')
        data = tablib.Dataset(headers=['ID', 'ProposalID', 'Title',
            'SpeakerUsername', 'SpeakerName', 'CoSpeakers', 'AudienceLevel',
            'Duration', 'Track'])
        for session in queryset:
            duration = session.duration
            audience_level = session.audience_level
            track = session.track
            cospeakers = [self._format_cospeaker(s) for s in session.additional_speakers.all()]
            data.append((
                session.pk,
                session.proposal.pk if session.proposal else "",
                session.title,
                session.speaker.user.username,
                unicode(session.speaker) if session.speaker else "",
                u"|".join(cospeakers),
                unicode(audience_level) if audience_level else "",
                unicode(duration) if duration else "",
                unicode(track) if track else "",
                ))
        return data


class GuidebookExporter(object):
    def __call__(self):
        result = []
        for session in models.Session.objects.select_related('track', 'location').all():
            result.append([
                session.title,
                session.start.date() if session.start else None,
                session.start.time() if session.start else None,
                session.end.time() if session.end else None,
                session.location.name if session.location else None,
                session.track.name if session.track else None,
                session.description
                ])
        for evt in models.SideEvent.objects.select_related('location').all():
            result.append([
                evt.name,
                evt.start.date() if evt.start else None,
                evt.start.time() if evt.start else None,
                evt.end.time() if evt.end else None,
                evt.location.name if evt.location else None,
                None,
                evt.description
                ])
        # Now sort by start date and time
        result.sort(cmp=self._sort_events)

        data = tablib.Dataset(headers=['title', 'date', 'start_time', 'end_time', 'location_name', 'track_name', 'description'])
        for evt in result:
            data.append(evt)
        return data
    
    def _sort_events(self, a, b):
        """
        Sort events by their start datetime. If these are similar, use the location
        name.
        """
        res =  cmp(a[1], b[1])
        if res == 0:
            res = cmp(a[2], b[2])
        if res == 0:
            res = cmp(a[4], b[4])
        return res

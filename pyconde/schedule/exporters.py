from . import models
from pyconde.sponsorship import models as sponsorship_models

import tablib


def _format_cospeaker(s):
    """
    Format the speaker's name for secondary speaker export and removes
    our separator characters to avoid confusion.
    """
    return unicode(s).replace("|", " ")


class SimpleSessionExporter(object):
    def __init__(self, queryset):
        self.queryset = queryset

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
            cospeakers = [_format_cospeaker(s) for s in session.additional_speakers.all()]
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
            cospeakers = [_format_cospeaker(s) for s in session.additional_speakers.all()]
            result.append([
                session.title,
                session.start.date() if session.start else '',
                session.start.time() if session.start else '',
                session.end.time() if session.end else '',
                session.location.name if session.location else '',
                session.track.name if session.track else '',
                session.description,
                session.kind.name if session.kind else u'Sonstiges',
                session.audience_level.name if session.audience_level else '',
                unicode(session.speaker),
                u"|".join(cospeakers),
                ])
        for evt in models.SideEvent.objects.select_related('location').all():
            loc = evt.location.name if evt.location else ''
            if evt.is_pause:
                loc = ''
            result.append([
                evt.name,
                evt.start.date() if evt.start else '',
                evt.start.time() if evt.start else '',
                evt.end.time() if evt.end else '',
                loc,
                '',
                evt.description,
                "Pause" if evt.is_pause else u'Sonstiges',
                '',  # audience level
                '',  # speaker
                '',  # co-speakers
                ])
        # Now sort by start date and time
        result.sort(cmp=self._sort_events)

        data = tablib.Dataset(headers=['title', 'date', 'start_time',
            'end_time', 'location_name', 'track_name', 'description', 'type',
            'audience', 'speaker', 'cospeakers'])
        for evt in result:
            data.append(evt)
        return data

    def _sort_events(self, a, b):
        """
        Sort events by their start datetime. If these are similar, use the location
        name.
        """
        res = cmp(a[1], b[1])
        if res == 0:
            res = cmp(a[2], b[2])
        if res == 0:
            res = cmp(a[4], b[4])
        return res


class GuidebookSponsorsExporter(object):
    def __call__(self):
        data = tablib.Dataset(headers=['name', 'website', 'description',
            'level_code', 'level_name'])
        for sponsor in sponsorship_models.Sponsor.objects.all():
            data.append([
                sponsor.name if sponsor.name else '',
                sponsor.external_url if sponsor.external_url else '',
                sponsor.description if sponsor.description else '',
                sponsor.level.slug if sponsor.level else '',
                sponsor.level.name if sponsor.level else '',
                ])
        return data

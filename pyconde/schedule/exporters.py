import tablib
import collections

from django.core.urlresolvers import reverse
from django.contrib.sites import models as site_models

from . import models
from pyconde.sponsorship import models as sponsorship_models
from pyconde.conference import models as conference_models


def _format_cospeaker(s):
    """
    Format the speaker's name for secondary speaker export and removes
    our separator characters to avoid confusion.
    """
    return unicode(s).replace("|", " ")


class AbstractExporter(object):
    def as_csv_value(self, value):
        """
        If a value is None, returns it as empty string instead of "None".
        """
        if value is None:
            return ""
        return value


class SimpleSessionExporter(AbstractExporter):
    def __init__(self, queryset):
        self.queryset = queryset

    def __call__(self):
        queryset = self.queryset.select_related('duration', 'track', 'proposal',
            'speaker', 'latest_proposalversion__track', 'audience_level')
        data = tablib.Dataset(headers=['ID', 'ProposalID', 'Title',
            'SpeakerUsername', 'SpeakerName', 'CoSpeakers', 'AudienceLevel',
            'Duration', 'Start', 'End', 'Track', 'Timeslots'])
        for session in queryset:
            duration = session.duration
            audience_level = session.audience_level
            track = session.track
            cospeakers = [_format_cospeaker(s) for s in session.additional_speakers.all()]
            row = [
                session.pk,
                session.proposal.pk if session.proposal else "",
                session.title,
                session.speaker.user.username,
                unicode(session.speaker) if session.speaker else "",
                u"|".join(cospeakers),
                unicode(audience_level) if audience_level else "",
                unicode(duration) if duration else "",
                unicode(session.start),
                unicode(session.end),
                unicode(track) if track else "",
            ]
            if session.proposal:
                row.append(
                    u'|'.join(unicode(slot)
                    for slot in session.proposal.available_timeslots.all()))
            else:
                row.append('')
            data.append(row)
        return data


class GuidebookExporter(object):
    def get_speaker_url(self, speaker):
        site = site_models.Site.objects.get_current()
        url = ""
        if speaker.user is not None:
            url = reverse('account_profile', kwargs={'uid': speaker.user.pk})
        return u'<https://{0}{1}>'.format(site.domain, url)

    def __call__(self):
        result = []
        for session in models.Session.objects.select_related('track', 'location').all():
            additional_speakers = list(session.additional_speakers.all())
            cospeakers = [_format_cospeaker(s) for s in additional_speakers]
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
                self.get_speaker_url(session.speaker),
                u" ".join([self.get_speaker_url(s) for s in additional_speakers]),
                session.abstract if session.abstract else '',
                ])
        for evt in models.SideEvent.current_conference.select_related('location').all():
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
                '',  # speaker url
                '',  # cospeaker urls
                '',  # abstract
                ])
        # Now sort by start date and time
        result.sort(cmp=self._sort_events)

        data = tablib.Dataset(headers=['title', 'date', 'start_time',
            'end_time', 'location_name', 'track_name', 'description', 'type',
            'audience', 'speaker', 'cospeakers', 'speaker_url',
            'cospeaker_urls', 'abstract'])
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


class GuidebookSectionsExporter(AbstractExporter):
    def __call__(self):
        data = tablib.Dataset(headers=['name', 'start', 'end', 'description'])
        for section in conference_models.Section.objects.order_by('start_date').all():
            data.append([
                self.as_csv_value(section.name),
                self.as_csv_value(section.start_date),
                self.as_csv_value(section.end_date),
                self.as_csv_value(section.description)
                ])
        return data


class SessionForEpisodesExporter(object):
    """
    This exporter creates a JSON file that is used by the video team in order
    to add metadata to the created media files.
    """

    def _get_speaker_data(self, session):
        Speaker = collections.namedtuple('Speaker', 'name email')
        result = []
        if session.speaker is not None:
            result.append(Speaker(unicode(session.speaker), session.speaker.user.email))
        for speaker in session.additional_speakers.all():
            result.append(Speaker(unicode(speaker), speaker.user.email))
        return result

    def create_episode_data(self, session):
        site = site_models.Site.objects.get_current()
        is_sideevent = isinstance(session, models.SideEvent)
        if is_sideevent:
            title = session.name
            speakers = []
            description = session.description
            released = True
        else:
            title = session.title
            speakers = self._get_speaker_data(session)
            description = session.abstract
            released = session.released

        ep = {
            'name': title,
            'room': session.location.name,
            'start': session.start.isoformat(),
            'duration': (session.end - session.start).total_seconds() / 60.0,
            'end': session.end.isoformat(),
            'authors': [s.name for s in speakers],
            'contact': [s.email for s in speakers],
            'released': released,
            'license': None,  # TODO: Add license information
            'description': description,
            'conf_key': "{0}:{1}".format("session" if not is_sideevent else "event", session.pk),
            'conf_url': u"https://{domain}{path}".format(domain=site.domain, path=session.get_absolute_url()),
            'tags': u", ".join([t.name for t in session.tags.all()]) if not is_sideevent else ""
        }
        return ep

    def __call__(self):
        items = [self.create_episode_data(session) for session in models.Session.current_conference.select_related('location', 'speaker').all()]
        # Also export all side-events that are not pauses
        items += [self.create_episode_data(evt) for evt in models.SideEvent.current_conference.filter(is_recordable=True).exclude(is_pause=True).select_related('location').all()]
        return items

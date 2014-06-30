# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime
import logging
import os
import shutil
import tablib
import StringIO

from itertools import chain, groupby
from operator import attrgetter

from lxml import etree

from django.core.urlresolvers import reverse
from django.contrib.sites import models as site_models
from django.template.defaultfilters import slugify
from django.utils.encoding import force_text
from django.utils.timezone import now

from . import models
from pyconde.sponsorship import models as sponsorship_models
from pyconde.conference import models as conference_models
from pyconde.accounts.utils import get_full_name


LOG = logging.getLogger('pyconde.schedule.exporters')


def _format_cospeaker(s):
    """
    Format the speaker's name for secondary speaker export and removes
    our separator characters to avoid confusion.
    """
    return force_text(s).replace('|', ' ')


class AbstractExporter(object):
    def as_csv_value(self, value):
        """
        If a value is None, returns it as empty string instead of 'None'.
        """
        if value is None:
            return ''
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
                session.proposal.pk if session.proposal else '',
                session.title,
                session.speaker.user.username,
                force_text(session.speaker) if session.speaker else '',
                '|'.join(cospeakers),
                force_text(audience_level) if audience_level else '',
                force_text(duration) if duration else '',
                force_text(session.start),
                force_text(session.end),
                force_text(track) if track else '',
            ]
            if session.proposal:
                row.append(
                    '|'.join(force_text(slot)
                    for slot in session.proposal.available_timeslots.all()))
            else:
                row.append('')
            data.append(row)
        return data


class GuidebookExporterSections(AbstractExporter):
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


class GuidebookExporterSessions(object):
    def get_speaker_url(self, speaker):
        site = site_models.Site.objects.get_current()
        url = ''
        if speaker.user is not None:
            url = reverse('account_profile', kwargs={'uid': speaker.user.pk})
        return '<https://{0}{1}>'.format(site.domain, url)

    def __call__(self):
        result = []
        sessions = models.Session.objects \
            .select_related('kind', 'audience_level', 'track',
                            'speaker__user__profile') \
            .prefetch_related('additional_speakers__user__profile',
                              'location') \
            .filter(released=True, start__isnull=False, end__isnull=False) \
            .order_by('start') \
            .only('end', 'start', 'title', 'abstract', 'description', 'is_global',
                  'kind__name',
                  'audience_level__name',
                  'track__name',
                  'speaker__user__username',
                  'speaker__user__profile__avatar',
                  'speaker__user__profile__full_name',
                  'speaker__user__profile__display_name',
                  'speaker__user__profile__short_info',
                  'speaker__user__profile__user') \
            .all()
        for session in sessions:
            additional_speakers = list(session.additional_speakers.all())
            cospeakers = [_format_cospeaker(s) for s in additional_speakers]
            result.append([
                session.title,
                session.start.date(),
                session.start.time(),
                session.end.time(),
                session.location_guidebook or '',
                session.track.name if session.track else '',
                session.abstract_rendered.encode('utf-8'),
                session.kind.name if session.kind else '',
                session.audience_level.name if session.audience_level else '',
                force_text(session.speaker),
                '|'.join(cospeakers),
                self.get_speaker_url(session.speaker),
                ' '.join([self.get_speaker_url(s) for s in additional_speakers]),
                session.description_rendered.encode('utf-8'),
                ])
        side_events = models.SideEvent.objects \
            .prefetch_related('location') \
            .filter(start__isnull=False, end__isnull=False) \
            .order_by('start') \
            .all()
        for evt in side_events:
            loc = evt.location_guidebook or ''
            if evt.is_pause:
                loc = ''
            result.append([
                evt.name,
                evt.start.date() if evt.start else '',
                evt.start.time() if evt.start else '',
                evt.end.time() if evt.end else '',
                loc,
                '',
                evt.description_rendered.encode('utf-8'),
                'Break' if evt.is_pause else '',  # kind
                '',  # audience level
                '',  # speaker
                '',  # co-speakers
                '',  # speaker url
                '',  # cospeaker urls
                '',  # abstract
                ])
        # Now sort by start date and time
        result.sort(cmp=self._sort_events)

        data = tablib.Dataset(headers=['Session Title', 'Date', 'Time Start',
            'Time End', 'Room/Location', 'Schedule Track (Optional)',
            'Description (Optional)', 'type', 'audience', 'speaker',
            'cospeakers', 'speaker_url', 'cospeaker_urls', 'description'])
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


class GuidebookExporterSpeakers(object):
    def __call__(self):
        data = tablib.Dataset(headers=['Name',
            'Sub-Title (i.e. Location, Table/Booth, or Title/Sponsorship Level)',
            'Description (Optional)', 'Location/Room'])
        speakers = set()
        sessions = models.Session.objects \
            .select_related('speaker__user__profile') \
            .prefetch_related('additional_speakers__user__profile') \
            .filter(released=True, start__isnull=False, end__isnull=False) \
            .only('speaker__user__username',
                  'speaker__user__profile__avatar',
                  'speaker__user__profile__full_name',
                  'speaker__user__profile__display_name',
                  'speaker__user__profile__short_info',
                  'speaker__user__profile__user') \
            .all()
        for session in sessions:
            user = session.speaker.user
            speakers.add((get_full_name(user), user.profile.short_info_rendered))
            for speaker in session.additional_speakers.all():
                user = speaker.user
                speakers.add((get_full_name(user), user.profile.short_info_rendered))

        speakers = sorted(speakers)
        for speaker in speakers:
            data.append([
                speaker[0],
                '',
                speaker[1].encode('utf-8'),
                ''
                ])
        return data


class GuidebookExporterSpeakerLinks(object):
    def __call__(self):
        data = tablib.Dataset(headers=['Session ID (Optional)',
            'Session Name (Optional)', 'Link To Session ID (Optional)',
            'Link To Session Name (Optional)', 'Link To Item ID (Optional)',
            'Link To Item Name (Optional)', 'Link To Form Name (Optional)'])
        sessions = models.Session.objects \
            .select_related('speaker__user__profile') \
            .prefetch_related('additional_speakers__user__profile') \
            .filter(released=True, start__isnull=False, end__isnull=False) \
            .only('title',
                  'speaker__user__username',
                  'speaker__user__profile__avatar',
                  'speaker__user__profile__full_name',
                  'speaker__user__profile__display_name',
                  'speaker__user__profile__user') \
            .all()

        for session in sessions:
            user = session.speaker.user
            speakers = set([get_full_name(user)])
            for speaker in session.additional_speakers.all():
                speakers.add(get_full_name(user))
            data.append([
                '',
                session.title,
                '',
                '',
                '',
                ';'.join(speakers),
                ''
                ])
        return data


class GuidebookExporterSponsors(object):
    def __call__(self):
        data = tablib.Dataset(headers=['name', 'website', 'description',
            'level_code', 'level_name'])
        for sponsor in sponsorship_models.Sponsor.objects.filter(active=True).all():
            data.append([
                sponsor.name if sponsor.name else '',
                sponsor.external_url if sponsor.external_url else '',
                sponsor.description_rendered if sponsor.description else '',
                sponsor.level.slug if sponsor.level else '',
                sponsor.level.name if sponsor.level else '',
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
            result.append(Speaker(force_text(session.speaker), session.speaker.user.email))
        for speaker in session.additional_speakers.all():
            result.append(Speaker(force_text(speaker), speaker.user.email))
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
            'conf_key': '{0}:{1}'.format('session' if not is_sideevent else 'event', session.pk),
            'conf_url': 'https://{domain}{path}'.format(domain=site.domain, path=session.get_absolute_url()),
            'tags': ', '.join([t.name for t in session.tags.all()]) if not is_sideevent else ''
        }
        return ep

    def __call__(self):
        items = [self.create_episode_data(session) for session in models.Session.current_conference.select_related('location', 'speaker').all()]
        # Also export all side-events that are not pauses
        items += [self.create_episode_data(evt) for evt in models.SideEvent.current_conference.filter(is_recordable=True).exclude(is_pause=True).select_related('location').all()]
        return items


class XMLExporter(object):

    def __init__(self, outfile, base_url=None, pretty=False, export_avatars=False):
        if base_url is None:
            self.base_url = 'http://%s' % site_models.Site.objects.get_current().domain
        else:
            self.base_url = base_url
        self.outfile = outfile
        self.event_sorter = attrgetter('start', 'end')
        self.day_grouper = lambda evt: evt.start.date()
        self.pretty = pretty
        self.export_avatars = export_avatars

    def export(self):
        if self.export_avatars:
            self.avatar_dir = os.path.splitext(self.outfile)[0]
            if not os.path.exists(self.avatar_dir):
                os.makedirs(self.avatar_dir)
        with open(self.outfile, 'w') as fp:
            with etree.xmlfile(fp) as xf:
                sessions = models.Session.objects \
                    .select_related('kind', 'audience_level', 'track',
                                    'speaker__user__profile') \
                    .prefetch_related('additional_speakers__user__profile',
                                      'location') \
                    .filter(released=True, start__isnull=False, end__isnull=False) \
                    .order_by('start') \
                    .only('end', 'start', 'title', 'abstract', 'description', 'is_global',
                          'kind__name',
                          'audience_level__name',
                          'track__name',
                          'speaker__user__username',
                          'speaker__user__profile__avatar',
                          'speaker__user__profile__full_name',
                          'speaker__user__profile__display_name',
                          'speaker__user__profile__short_info',
                          'speaker__user__profile__user') \
                    .all()
                side_events = models.SideEvent.objects \
                    .prefetch_related('location') \
                    .filter(start__isnull=False, end__isnull=False) \
                    .order_by('start') \
                    .all()
                all_events = sorted(chain(sessions, side_events), key=self.event_sorter)
                all_events = groupby(all_events, self.day_grouper)
                with xf.element('schedule', created=now().isoformat()):
                    for day, events in all_events:
                        self._export_day(fp, xf, day, events)

    def _export_day(self, fp, xf, day, events):
        with xf.element('day', date=day.isoformat()):
            for event in events:
                try:
                    if isinstance(event, models.Session):
                        self._export_session(fp, xf, event)
                    elif isinstance(event, models.SideEvent):
                        self._export_side_event(fp, xf, event)
                except Exception as e:
                    LOG.fatal('Error exporting %s(%d) %s' % (
                        event.__class__.__name__, event.id, event) + force_text(e))
                    import traceback
                    traceback.print_exc()

    def _export_session(self, fp, xf, event):
        with xf.element('entry', id=force_text(event.id)):
            with xf.element('category'):
                xf.write(force_text(event.kind), pretty_print=self.pretty)
            with xf.element('audience'):
                xf.write(force_text(event.audience_level), pretty_print=self.pretty)
            with xf.element('topics'):
                if event.track:
                    with xf.element('topic'):
                        xf.write(force_text(event.track), pretty_print=self.pretty)
            with xf.element('start'):
                xf.write(event.start.strftime('%H%M'), pretty_print=self.pretty)
            with xf.element('duration'):
                dur = int((event.end - event.start).total_seconds() / 60)
                xf.write(force_text(dur), pretty_print=self.pretty)

            rooms = event.location.all()
            if len(rooms) > 1:
                with xf.element('room'):
                    xf.write(event.location_pretty, pretty_print=self.pretty)
            elif len(rooms) == 1:
                with xf.element('room', id=force_text(rooms[0].id)):
                    xf.write(event.location_pretty, pretty_print=self.pretty)
            elif event.is_global:
                with xf.element('room'):
                    xf.write('ALL', pretty_print=self.pretty)
            else:
                with xf.element('room'):
                    pass

            with xf.element('title'):
                xf.write(force_text(event.title), pretty_print=self.pretty)
            with xf.element('abstract'):
                xf.write(force_text(event.abstract), pretty_print=self.pretty)
            with xf.element('description'):
                xf.write(force_text(event.description), pretty_print=self.pretty)
            with xf.element('speakers'):
                self._export_speaker(fp, xf, event.speaker.user)
                for speaker in event.additional_speakers.all():
                    self._export_speaker(fp, xf, speaker.user)

    def _export_side_event(self, fp, xf, event):
        with xf.element('entry', id=force_text(event.id)):
            with xf.element('category'):
                pass
            with xf.element('audience'):
                pass
            with xf.element('topics'):
                pass
            with xf.element('start'):
                xf.write(event.start.strftime('%H%M'), pretty_print=self.pretty)
            with xf.element('duration'):
                dur = int((event.end - event.start).total_seconds() / 60)
                xf.write(force_text(dur), pretty_print=self.pretty)

            rooms = event.location.all()
            if len(rooms) > 1:
                with xf.element('room'):
                    xf.write(event.location_pretty, pretty_print=self.pretty)
            elif len(rooms) == 1:
                with xf.element('room', id=force_text(rooms[0].id)):
                    xf.write(event.location_pretty, pretty_print=self.pretty)
            elif event.is_global:
                with xf.element('room'):
                    xf.write('ALL', pretty_print=self.pretty)
            else:
                with xf.element('room'):
                    pass

            with xf.element('title'):
                xf.write(event.name, pretty_print=self.pretty)
            with xf.element('description'):
                xf.write(event.description, pretty_print=self.pretty)
            with xf.element('speakers'):
                pass

    def _export_speaker(self, fp, xf, user):
        profile = user.profile
        with xf.element('speaker', id=force_text(user.id)):
            with xf.element('name'):
                name = get_full_name(user)
                xf.write(name, pretty_print=self.pretty)
            with xf.element('profile'):
                xf.write(self.base_url + reverse('account_profile',
                                                 kwargs={'uid': user.id}), pretty_print=self.pretty)
            with xf.element('description'):
                xf.write(user.profile.short_info, pretty_print=self.pretty)
            with xf.element('image'):
                if profile.avatar:
                    avatar_url = self.base_url + profile.avatar.url
                    xf.write(avatar_url, pretty_print=self.pretty)
                if self.export_avatars:
                    filename, ext = os.path.splitext(profile.avatar.file.name)
                    dest = os.path.join(self.avatar_dir, str(user.id)) + ext
                    shutil.copy(profile.avatar.file.name, dest)


class XMLExporterPentabarf(object):

    def __init__(self):
        self.domain = site_models.Site.objects.get_current().domain
        self.base_url = 'http://%s' % self.domain

    def export(self):
        output = StringIO.StringIO()
        with etree.xmlfile(output) as xf:
            sessions = models.Session.objects \
                .select_related('kind', 'audience_level', 'track',
                                'speaker__user__profile') \
                .prefetch_related('additional_speakers__user__profile',
                                  'location') \
                .filter(released=True, start__isnull=False, end__isnull=False,
                        kind__slug__in=('talk', 'keynote')) \
                .order_by('start') \
                .only('end', 'start', 'title', 'abstract', 'description', 'language',
                      'kind__name',
                      'audience_level__name',
                      'track__name',
                      'speaker__user__username',
                      'speaker__user__profile__avatar',
                      'speaker__user__profile__full_name',
                      'speaker__user__profile__display_name',
                      'speaker__user__profile__short_info',
                      'speaker__user__profile__user') \
                .all()
            self.conference = force_text(conference_models.current_conference())
            self._duration_base = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0))
            with xf.element('iCalendar'):
                with xf.element('vcalendar'):
                    with xf.element('version'):
                        xf.write('2.0')
                    with xf.element('prodid'):
                        xf.write('-//Pentabarf//Schedule %s//EN' % self.conference)
                    with xf.element('x-wr-caldesc'):
                        xf.write(self.conference)
                    with xf.element('x-wr-calname'):
                        xf.write(self.conference)
                    for session in sessions:
                        self._export_session(xf, session)
        return output

    def _export_session(self, xf, session):
        with xf.element('vevent'):
            with xf.element('method'):
                xf.write('PUBLISH')
            with xf.element('uid'):
                xf.write('%d@%s@%s' % (session.id, self.conference, self.domain))
            with xf.element('{http://pentabarf.org}event-id'):
                xf.write(force_text(session.id))
            with xf.element('{http://pentabarf.org}event-slug'):
                xf.write(slugify(session.title))
            with xf.element('{http://pentabarf.org}title'):
                xf.write(session.title)
            with xf.element('{http://pentabarf.org}subtitle'):
                xf.write('')
            with xf.element('{http://pentabarf.org}language'):
                xf.write(session.get_language_display())
            with xf.element('{http://pentabarf.org}language-code'):
                xf.write(session.language)
            with xf.element('dtstart'):
                xf.write(session.start.strftime('%Y%m%dT%H%M%S'))
            with xf.element('dtend'):
                xf.write(session.end.strftime('%Y%m%dT%H%M%S'))
            with xf.element('dtend'):
                duration = self._duration_base + (session.end - session.start)
                xf.write(duration.strftime('%HH%MM%SS'))
            with xf.element('summary'):
                xf.write(session.title)
            with xf.element('description'):
                xf.write(session.abstract_rendered)
            with xf.element('class'):
                xf.write('PUBLIC')
            with xf.element('status'):
                xf.write('CONFIRMED')
            with xf.element('category'):
                xf.write(force_text(session.kind))
            with xf.element('url'):
                xf.write(session.get_absolute_url())
            for location in session.location.all():
                with xf.element('location'):
                    xf.write(force_text(location))
            with xf.element('attendee'):
                xf.write(get_full_name(session.speaker.user))
            for cospeaker in session.additional_speakers.all():
                with xf.element('attendee'):
                    xf.write(get_full_name(session.speaker.user))

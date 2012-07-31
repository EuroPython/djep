import tablib
import itertools
import math
import datetime
import collections

from pyconde.conference import models as conference_models

from . import models

from django.core.cache import cache


def proposal_is_scheduled(proposal):
    """
    Checks if a given proposal already has a session associated with it.

    Warning: This internally caches the result for 10 seconds.
    """
    proposal_pks = cache.get('proposal_pks_with_session')
    if proposal_pks is None:
        proposal_pks = set([o['proposal__pk'] for o in models.Session.objects.values('proposal__pk')])
        cache.set('proposal_pks_with_session', proposal_pks, 10)
    return proposal.pk in proposal_pks


def create_simple_export(queryset):
    def _format_cospeaker(s):
        """
        Format the speaker's name for secondary speaker export and removes
        our separator characters to avoid confusion.
        """
        return unicode(s).replace("|", " ")

    queryset = queryset.select_related('duration', 'track', 'proposal',
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
            session.proposal.pk,
            session.title,
            session.speaker.user.username,
            unicode(session.speaker) if session.speaker else "",
            u"|".join(cospeakers),
            unicode(audience_level) if audience_level else "",
            unicode(duration) if duration else "",
            unicode(track) if track else "",
            ))
    return data


def create_schedule(row_duration=30):
    """
    Creates a schedule for each section of the conference.

    @param row_duration duration represented by a row in minutes
    """
    result = {}
    for section in conference_models.Section.objects.all():
        section_schedule = create_section_schedule(section,
            row_duration=row_duration)
        result[section] = section_schedule
    return result


def create_section_schedule(section, row_duration=30):
    # Determine all the locations used by this section
    sessions = list(section.sessions
        .select_related('location')
        .order_by('start')
        .all())
    side_events = list(section.side_events\
        .select_related('location')
        .order_by('start')
        .all())

    locations = set()
    for session in sessions:
        locations.add(session.location)
    for evt in side_events:
        # Global events span all session locations and therefor the location
        # should not be included in the columns list
        if evt.is_global:
            continue
        locations.add(evt.location)
    locations = sorted(locations, cmp=lambda a, b: a.order - b.order)

    events = sorted(itertools.chain(sessions, side_events),
        cmp=_evt_start_cmp)
    if not events:
        return {}
    start_time = events[0].start
    end_time = events[-1].end
    grid = _create_base_grid(start_time, end_time, row_duration)
    for evt in events:
        # Normalize date for the grid
        grid[evt.start].append(GridCell(evt, (evt.end - evt.start).total_seconds() / (row_duration * 60)))
    # Now sort by location order in order to being able to render the grid as
    # HTML
    new_grid = []
    for k, v in grid.iteritems():
        v.sort(cmp=_gridcell_location_cmp)
        new_grid.append(GridRow(k, v))
    new_grid.sort(cmp=lambda a, b: cmp(a.date, b.date))

    # Split the whole section grid into days
    current_day = None
    days = []
    for row in new_grid:
        if current_day is None:
            current_day = SectionDay(row.date.date(), [])
        elif current_day.day > row.date.date():
            days.append(current_day)
            current_day = SectionDay(row.date.date(), [])
        current_day.rows.append(row)
    if current_day and current_day.rows:
        days.append(current_day)
    return (locations, days)


GridRow = collections.namedtuple('GridRow', ['date', 'events'])
GridCell = collections.namedtuple('GridCell', ['event', 'rowspan'])
SectionDay = collections.namedtuple('SectionDay', ['day', 'rows'])


def _create_base_grid(start_time, end_time, row_duration):
    t = start_time
    grid = {}
    while t < end_time:
        grid[t] = []
        t = t + datetime.timedelta(0, row_duration * 60)
    return grid


def _get_number_of_rows(all_events, row_duration=30):
    events = sorted(all_events, cmp=_evt_start_cmp)
    start_time = events[0].start
    end_time = events[-1].end
    section_duration = end_time - start_time
    section_duration_minutes = (section_duration.days * 24 * 60) + (section_duration.seconds / 60)
    return math.ceil(float(section_duration_minutes) / row_duration)


def _evt_start_cmp(a, b):
    return int((a.start - b.start).total_seconds())


def _gridcell_location_cmp(a, b):
    return a.event.location.order - b.event.location.order

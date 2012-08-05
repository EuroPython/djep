import tablib
import itertools
import math
import datetime
from  django.utils.datastructures import SortedDict

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
    result = SortedDict()
    for section in conference_models.Section.objects.order_by('order', 'start_date').all():
        section_schedule = create_section_schedule(section,
            row_duration=row_duration)
        result[section] = section_schedule
    return result


def create_section_schedule(section, row_duration=30):
    # Determine all the locations used by this section
    sessions = list(section.sessions
        .select_related('location', 'audience_level', 'speaker', 'track')
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
        grid[evt.start].append(GridCell(evt, int((evt.end - evt.start).total_seconds() / (row_duration * 60))))
    # Now sort by location order in order to being able to render the grid as
    # HTML
    new_grid = []
    for k, v in grid.iteritems():
        v.sort(cmp=_gridcell_location_cmp)
        new_grid.append(GridRow(k, k + datetime.timedelta(0, row_duration * 60), v))
    new_grid.sort(cmp=lambda a, b: cmp(a.start, b.start))

    # Split the whole section grid into days
    current_day = None
    days = []
    prev_row = None
    for row in new_grid:
        if current_day is None:
            current_day = SectionDay(row.start.date(), [])
        elif current_day.day < row.start.date():
            days.append(current_day)
            current_day = SectionDay(row.start.date(), [])
        current_day.rows.append(row)
        # Propagate pause rows if necessary
        if prev_row is not None:
            if prev_row.is_pause_row() and not row.events:
                if prev_row.events:
                    prev_row.pause_until = prev_row.events[0].end
                if prev_row.pause_until is not None and prev_row.pause_until >= row.end:
                    row.pause = True
                    row.pause_until = prev_row.pause_until
        prev_row = row
    if current_day and current_day.rows:
        days.append(current_day)
    # Strip out heading and tailing empty rows
    for day in days:
        day.rows = _strip_empty_rows(day.rows)
    return (locations, days)


class GridRow(object):
    def __init__(self, start, end, events):
        self.start = start
        self.end = end
        self.events = events
        self.pause = None
        self.pause_until = None

    def is_pause_row(self):
        if self.pause is not None:
            return self.pause
        return len(self.events) == 1 and self.events[0].is_global and self.events[0].is_pause

    def __str__(self):
        return "<GridRow %s - %s>" % (self.start, self.end)

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)


class GridCell(object):
    def __init__(self, event, rowspan):
        self.rowspan = rowspan
        self.speakers = []
        self.track_name = None
        self.name = None
        self.url = ""
        self.is_global = False
        self.is_pause = False
        self.start = None
        self.end = None
        self.level_name = None
        if event is not None:
            self.event = event
            self.type = event.__class__.__name__.lower()
            if hasattr(event, 'get_absolute_url'):
                self.url = event.get_absolute_url()
            self.start = event.start
            self.end = event.end
            if isinstance(event, models.Session):
                self.name = event.title
                if event.speaker:
                    self.speakers.append(unicode(event.speaker))
                for speaker in event.additional_speakers.select_related('user').all():
                    self.speakers.append(unicode(speaker))
                if event.track:
                    self.track_name = event.track.name
                if event.audience_level:
                    self.level_name = event.audience_level.name
            else:
                self.is_global = event.is_global
                self.is_pause = event.is_pause
                self.name = event.name


class SectionDay(object):
    def __init__(self, day, rows):
        self.day = day
        self.rows = rows


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


def _strip_empty_rows(rows):
    first_idx_with_events = None
    last_idx_with_events = None
    rows_until = None
    for idx, row in enumerate(rows):
        if first_idx_with_events is None and row.events:
            first_idx_with_events = idx
        if first_idx_with_events is not None and row.events:
            last_idx_with_events = idx
            for evt in row.events:
                if rows_until is None or evt.end > rows_until:
                    rows_until = evt.end
        if last_idx_with_events is not None and not row.events and row.end <= rows_until:
            last_idx_with_events = idx
    if not first_idx_with_events:
        first_idx_with_events = 0
    if not last_idx_with_events:
        last_idx_with_events = first_idx_with_events - 1
    return rows[first_idx_with_events:last_idx_with_events + 1]

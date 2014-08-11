import itertools
import math
import datetime
import collections
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.timezone import now

from ..conference import models as conference_models

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


def create_schedule(row_duration=30, uncached=None, merge_sections=False):
    """
    Creates a schedule for each section of the conference.

    @param row_duration duration represented by a row in minutes
    """
    if uncached is None:
        uncached = not getattr(settings, 'SCHEDULE_CACHE_SCHEDULE', True)
    conf = conference_models.current_conference()
    cache_key = 'schedule:{0}:{1}'.format(conf.pk, row_duration)
    if not uncached:
        result = cache.get(cache_key)
        if result:
            return result
    result = SortedDict()
    if merge_sections:
        section_schedule = create_section_schedule(None,
            row_duration=row_duration, uncached=uncached)
        result['merged'] = section_schedule
    else:
        for section in conference_models.Section.objects.order_by('order', 'start_date').all():
            section_schedule = create_section_schedule(section,
                row_duration=row_duration, uncached=uncached)
            result[section] = section_schedule
    if not uncached:
        cache.set(cache_key, result, settings.SCHEDULE_CACHE_TIMEOUT)
    return result


def create_section_schedule(section, row_duration=30, uncached=False):
    """
    Creates a schedule for a given section.

    @param section section for which the schedule should be generated.
    @param row_duration number of minutes a single row should represent
    """
    if section is None:
        schedule_cache_key = 'section_schedule:__merged__:{0}'.format(row_duration)
    else:
        schedule_cache_key = 'section_schedule:{0}:{1}'.format(section.pk, row_duration)

    if not uncached:
        section_schedule = cache.get(schedule_cache_key)
        if section_schedule:
            return section_schedule

    if section is None:
        sessions = models.Session.objects
        side_events = models.SideEvent.objects
    else:
        sessions = section.sessions
        side_events = section.side_events

    sessions = sessions.select_related('audience_level',
                                       'track',
                                       'kind',
                                       'speaker__user__profile',
                                       'conference') \
                       .prefetch_related('additional_speakers__user__profile',
                                         'location') \
                       .filter(released=True, start__isnull=False, end__isnull=False) \
                       .order_by('start') \
                       .all()
    side_events = side_events.prefetch_related('location') \
                             .filter(start__isnull=False, end__isnull=False) \
                             .order_by('start') \
                             .all()

    evt_cache = {}

    locations = set()
    start_time = None
    end_time = None
    for session in sessions:
        start_time = session.start if start_time is None else min(start_time, session.start)
        end_time = session.end if end_time is None else max(end_time, session.end)
        if session.is_global:
            continue
        locations |= set(session.location.all())
    for evt in side_events:
        start_time = evt.start if start_time is None else min(start_time, evt.start)
        end_time = evt.end if end_time is None else max(end_time, evt.end)
        # Global events span all session locations and therefor the location
        # should not be included in the columns list
        if evt.is_global:
            continue
        locations |= set(evt.location.all())
    locations = sorted(locations, cmp=lambda a, b: a.order - b.order)

    # This allows overriding sessions (e.g. posters) with side events in the
    # schedule table but still have them listed in the general lists.
    events = sorted(itertools.chain(sessions, side_events),
        cmp=_evt_start_cmp)

    if not events:
        return {}

    # As a first step we build a grid with the respective row start time as
    # key and fill it with events starting at that time.
    grid = _create_base_grid(start_time, end_time, row_duration)
    for evt in events:
        cell = GridCell(evt, int((evt.end - evt.start).total_seconds() / (row_duration * 60)))
        evt_cache[repr(cell)] = cell
        grid[evt.start].append(cell)

    # Convert this grid into a list of grid rows sorted by the row's start time.
    new_grid = []
    for k, v in grid.iteritems():
        new_grid.append(GridRow(k, k + datetime.timedelta(0, row_duration * 60), v))
    new_grid.sort(cmp=lambda a, b: cmp(a.start, b.start))

    # Split the whole section grid into days
    current_day = None
    days = []
    prev_row = None
    for row in new_grid:
        _pad_row_for_locations(row, prev_row, locations)

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
    has_active = False
    for day in days:
        day.rows = _strip_empty_rows(day.rows)
        day.rows = _merge_adjacent_row_cells(day.rows)
        if day.active:
            has_active = True
    if days and not has_active:
        days[0].active = True

    if not uncached:
        cache.set(schedule_cache_key, (locations, days), settings.SCHEDULE_CACHE_TIMEOUT)
    return (locations, days)


class GridRow(object):
    def __init__(self, start, end, events):
        self.start = start
        self.end = end
        self.events = events
        self.pause = None
        self.pause_until = None
        self.event_by_location = {}
        self.cells = events
        for evt in events:
            if not evt.event or not evt.event.location:
                continue
            for loc in evt.event.location.all():
                self.event_by_location[loc] = evt

    def is_pause_row(self):
        if self.pause is not None:
            return self.pause
        return self.is_global_row() and self.events[0].is_pause

    def is_global_row(self):
        return len(self.events) == 1 and self.events[0].is_global

    def __str__(self):
        return "<GridRow %s - %s>" % (self.start, self.end)

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.cells)

    def reorder_by_location(self, locations):
        events = [self.event_by_location[loc] for loc in locations]
        self.cells = events

    @property
    def contains_global(self):
        if self.is_pause_row():
            return True
        for evt in self.events:
            if evt.is_global:
                return True
        return False

    def get_renderable_cells(self):
        """
        Returns all cells that are either empty or represent events. Pure
        fillers are skipped
        """
        return (c for c in self.cells if c.is_empty or not c.is_filler)


class GridCell(object):
    """
    A cell prepresents an element within a row that can either be an actual
    event or a placeholder for an event in the same room that hasn't yet ended
    or a completely empty placeholder.
    """

    def __init__(self, event, rowspan, colspan=1):
        self.is_filler = False
        self.rowspan = rowspan
        self.colspan = colspan
        self.speakers = []
        self.track_name = None
        self.name = None
        self.url = ""
        self.is_global = False
        self.is_pause = False
        self.start = None
        self.end = None
        self.level = 0
        self.level_name = None
        self.language = None
        self.location = event.location if event else None
        self.icon = None
        if isinstance(self.location, conference_models.Location):
            self.location = [self.location]
        elif hasattr(self.location, 'all'):
            self.location = self.location.all()
        self.event = None
        self.type = None
        self.session_kind = None
        if event is not None:
            self.event = event
            if hasattr(event, 'get_absolute_url'):
                self.url = event.get_absolute_url()
            self.start = event.start
            self.end = event.end
            if isinstance(event, models.Session):
                self.name = event.title
                self.type = 'session'
                self.session_kind = self.event.kind.slug if self.event.kind else None
                self.is_global = event.is_global
                if event.speaker:
                    self.speakers.append(unicode(event.speaker))
                for speaker in event.additional_speakers.all():  # .select_related('user__profile')
                    self.speakers.append(unicode(speaker))
                if event.track:
                    self.track_name = event.track.name
                if event.audience_level:
                    self.level_name = event.audience_level.name
                    self.level = event.audience_level.level
                if event.language:
                    self.language = event.get_language_display()
            else:
                self.type = 'sideevent'
                self.is_global = event.is_global
                self.is_pause = event.is_pause
                self.icon = event.icon
                self.name = event.name

    @property
    def is_empty(self):
        return self.is_filler and not self.event

    def __str__(self):
        if self.is_empty:
            return '<GridCell EMTPY location=%s>' % (self.location,)
        elif self.is_filler:
            return '<GridCell FILLER location=%s>' % (self.location,)
        else:
            return '<GridCell location=%s start=%s end=%s evt=%s>' % (self.location, self.start, self.end, self.event)

    __repr__ = __str__

    def repr(self):
        type_ = 'session' if isinstance(self.event, models.Session) else 'side'
        return '{0}:{1}'.format(type_, self.event.pk)


class SectionDay(object):
    def __init__(self, day, rows):
        self.day = day
        self.rows = rows
        self.active = (self.day == now().date())


def _create_base_grid(start_time, end_time, row_duration):
    """
    Create the initial grid with a row for every time interval as defined
    by the start_time, end_time and the duration in minutes specified.
    """
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
    """
    Removes empty rows at the end and beginning of the rows collections and
    returns the result.
    """
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


def _pad_row_for_locations(row, prev_row, locations):
    """
    Make sure that "empty" rooms are also included in the grid as such.
    This has to take into account if a talk in the same room in the
    previous row actually requires a row-span. If it does, *this* row
    must not be empty, otherwise it has to include an empty cell.
    """
    if row.contains_global:
        return
    for location in locations:
        if location not in row.event_by_location:
            # Let's check the previous row if it exists. We also have to take
            # global events into account
            prev_event = prev_row.event_by_location.get(location, None) if prev_row else None
            if prev_event is None and prev_row is not None and prev_row.is_global_row():
                prev_event = prev_row.events[0]

            if prev_event is None or prev_event.is_empty:
                filler = GridCell(None, 1)
            elif prev_event.end <= row.start:
                filler = GridCell(None, 1)
            else:
                filler = GridCell(prev_event, 1)
            if not filler.start:
                filler.start = row.start
            if not filler.end:
                filler.end = row.end
            filler.location = location
            filler.is_filler = True
            row.event_by_location[location] = filler
    row.reorder_by_location(locations)


def _merge_adjacent_row_cells(rows):
    """
    Combines adjacent cells in the same row iff they belong to the same event.

    .. warning::

        This function cannot handle overlapping events in the same room, eg.

            A A
            A B

        will result in

            A A
            A A B

        meaning, there is a table column overhang.
    """
    for ridx, row in enumerate(rows):
        if len(row) < 1:
            continue
        start_cell = row.cells[0]
        for cidx, cell in enumerate(row.cells[1:], 1):
            if start_cell is cell:
                start_cell.colspan += 1
                row.cells[cidx] = None
            else:
                start_cell = cell
        row.cells = filter(None, row.cells)
    return rows


def can_edit_session(user, session):
    """
    Checks if a given user can modify the specified session.
    """
    if user.is_anonymous():
        return False
    if user.is_superuser or user.is_staff:
        return True
    speaker = user.speaker_profile
    if not speaker:
        return False
    if session.speaker == speaker:
        return True
    return speaker in session.additional_speakers.all()


def prepare_event(evt):
    model = None
    if isinstance(evt, basestring):
        type_, pk = evt.split(':')
        if type_ == 'side':
            model = models.SideEvent.current_conference.select_related('location').get(pk=pk)
        else:
            model = models.Session.current_conference.select_related('location').get(pk=pk)
    else:
        model = evt
    return GridCell(model, None)


def load_event_models(events):
    pk_map = collections.defaultdict(list)
    result = []
    for evt in events:
        type_, pk = evt.split(':')
        pk_map[type_].append(pk)
    for k, v in pk_map.iteritems():
        if k == 'session':
            result += list(models.Session.current_conference.select_related('location').filter(pk__in=v))
        if k == 'side':
            result += list(models.SideEvent.current_conference.select_related('location').filter(pk__in=v))
    return result

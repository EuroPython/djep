from django import template

from .. import models


register = template.Library()


@register.inclusion_tag('events/tags/list_events.html')
def list_events(number_of_events=None):
    events = models.Event.objects.all()
    if number_of_events is not None:
        events = events[:number_of_events]
    has_range = False
    for evt in events:
        if evt.end_date:
            has_range = True
            break
    return {
        'events': events,
        'has_range': has_range
    }

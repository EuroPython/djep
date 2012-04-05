import datetime

from django import template

from .. import models


register = template.Library()


@register.inclusion_tag('events/tags/list_events.html')
def list_events(number_of_events=3):
    now = datetime.datetime.now()
    return {
        'events': models.Event.objects.filter(date__gte=now).all()[:number_of_events]
    }

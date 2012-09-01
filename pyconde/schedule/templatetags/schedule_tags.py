import logging

from django.template import Library, Node, TemplateSyntaxError

from .. import utils
from .. import models

register = Library()
log = logging.getLogger(__name__)


@register.inclusion_tag('schedule/tags/event.html', takes_context=True)
def eventinfo(context, evt):
    event = None
    if isinstance(evt, basestring):
        if '_evt_cache' in context:
            event = context['_evt_cache'].get(evt)
        if event is None:
            event = utils.prepare_event(evt)
    else:
        event = evt
    return {
        'event': event
    }


class PreloadEventsNode(Node):
    def __init__(self, nodelist, event_names=None):
        self.nodelist = nodelist
        self.event_names = event_names or []

    def __repr__(self):
        return "<PreloadEventNode>"

    def render(self, context):
        cache = {}
        for evt in utils.load_event_models(self.event_names):
            if isinstance(evt, models.Session):
                evtkey = 'session:{0}'.format(evt.pk)
            else:
                evtkey = 'side:{0}'.format(evt.pk)
            cache[evtkey] = utils.prepare_event(evt)
        context.update({
            '_evt_cache': cache
            })
        output = self.nodelist.render(context)
        context.pop()
        return output


@register.tag('preloadevents')
def do_preloadevents(parser, token):
    bits = token.split_contents()
    event_names = bits[1:]
    if not event_names:
        raise TemplateSyntaxError("You have to specify at least one event")
    nodelist = parser.parse(('endpreloadevents',))
    parser.delete_first_token()
    return PreloadEventsNode(nodelist, event_names=event_names)

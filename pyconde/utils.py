from django.http import HttpResponseForbidden

from django.template.loader import render_to_string
from django.template import RequestContext


def create_403(request, msg=None):
    if msg is None:
        msg = _("You are not allowed to access this page.")
    return HttpResponseForbidden(render_to_string('403.html', {
            'msg': msg
        }, context_instance=RequestContext(request)))

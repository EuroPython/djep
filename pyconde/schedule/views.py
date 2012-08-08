from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from ..proposals import models as proposal_models
from ..conference import models as conference_models

from . import models
from . import utils


def view_schedule(request):
    return TemplateResponse(
        request=request,
        context={
            'schedule': utils.create_schedule()
            },
        template='schedule/schedule.html'
        )


def session_by_proposal(request, proposal_pk):
    """
    Redirects to a session page based on the given proposal pk or presents
    a temporary page if a proposal exists but no session could be found for it.
    """
    proposal = get_object_or_404(proposal_models.Proposal.objects,
        pk=proposal_pk)
    try:
        session = proposal.sessions.all()[0]
        return HttpResponseRedirect(session.get_absolute_url())
    except:
        return TemplateResponse(
            request=request,
            template='schedule/session_not_available.html',
            context={
                'proposal': proposal
            }
        )


def sessions_by_tag(request, tag):
    """
    Lists all talks with a given tag on a single page.
    """
    sessions = models.Session.objects.select_related('location')\
        .filter(tags__name=tag).order_by('title')
    return TemplateResponse(
        request=request,
        template='schedule/sessions_by_tag.html',
        context={
            'tag': tag,
            'sessions': sessions
        }
    )


def sessions_by_location(request, pk):
    """
    Lists all talks with a given tag on a single page.
    """
    location = get_object_or_404(conference_models.Location, pk=pk)
    sessions = models.Session.objects.select_related('location')\
        .filter(location=location).order_by('start')
    return TemplateResponse(
        request=request,
        template='schedule/sessions_by_location.html',
        context={
            'location': location,
            'sessions': sessions
        }
    )


def view_session(request, session_pk):
    """
    Renders all information available about a session.
    """
    session = get_object_or_404(models.Session, pk=session_pk)
    return TemplateResponse(
        request=request,
        context={
            'session': session
        },
        template='schedule/session.html'
    )

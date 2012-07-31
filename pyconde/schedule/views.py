from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from ..proposals import models as proposal_models

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


def view_session(request, session_pk):
    """
    Renders all information available about a session.
    """
    return TemplateResponse(
        request=request,
        template='schedule/session_not_available.html'
    )

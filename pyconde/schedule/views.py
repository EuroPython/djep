# -*- encoding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache

from ..proposals import models as proposal_models
from ..conference import models as conference_models
from ..utils import create_403

from . import models
from . import utils
from . import forms
from . import exporters


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
            'session': session,
            'can_edit': utils.can_edit_session(request.user, session)
        },
        template='schedule/session.html'
    )


def view_sideevent(request, pk):
    """
    Shows details of a specific side event.
    """
    evt = get_object_or_404(models.SideEvent, pk=pk)
    return TemplateResponse(
        request=request,
        context={
            'event': evt
        },
        template='schedule/sideevent.html'
    )


@login_required
def edit_session(request, session_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    if not utils.can_edit_session(request.user, session):
        return create_403()
    if request.method == 'POST':
        form = forms.EditSessionForm(instance=session, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Changes saved"))
            return HttpResponseRedirect(session.get_absolute_url())
    else:
        form = forms.EditSessionForm(instance=session)
    return TemplateResponse(
        request=request,
        context={
        'form': form,
        'session': session
        },
        template='schedule/edit_session.html'
    )


def guidebook_events_export(request):
    """
    A simple export of all events as it can be used for importing into
    Guidebook.
    """
    data = cache.get('schedule:guidebook:events', None)
    if not data:
        data = exporters.GuidebookExporter()().csv
        cache.set('schedule:guidebook:events', data)
    return HttpResponse(data,
        content_type='text/csv')

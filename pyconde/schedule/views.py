# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from ..proposals import models as proposal_models
from ..conference import models as conference_models
from ..utils import create_403

from . import models
from . import utils
from . import forms
from . import exporters

from .exceptions import AttendingError


def view_schedule(request):
    return TemplateResponse(
        request=request,
        context={
            'schedule': utils.create_schedule(row_duration=15, merge_sections=True)
        },
        template='schedule/schedule.html'
    )


def session_by_proposal(request, proposal_pk):
    """
    Redirects to a session page based on the given proposal pk or presents
    a temporary page if a proposal exists but no session could be found for it.
    """
    proposal = get_object_or_404(proposal_models.Proposal.current_conference,
        pk=proposal_pk)
    try:
        session = proposal.sessions.all()[0]
        return HttpResponseRedirect(session.get_absolute_url())
    except IndexError:
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
    sessions = models.Session.objects.select_related('speaker__user__profile') \
                                     .prefetch_related('location') \
                                     .filter(released=True, tags__name=tag) \
                                     .order_by('title') \
                                     .all()
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
    sessions = models.Session.objects.select_related('speaker__user__profile') \
                                     .prefetch_related('location') \
                                     .filter(released=True, location=location) \
                                     .order_by('start') \
                                     .all()
    return TemplateResponse(
        request=request,
        template='schedule/sessions_by_location.html',
        context={
            'location': location,
            'sessions': sessions
        }
    )


def sessions_by_kind(request, pk):
    """
    Lists all talks with a given tag on a single page.
    """
    kind = get_object_or_404(conference_models.SessionKind, pk=pk)
    sessions = models.Session.objects.select_related('speaker__user__profile') \
                                     .prefetch_related('location') \
                                     .filter(released=True, kind=kind) \
                                     .order_by('title') \
                                     .all()
    return TemplateResponse(
        request=request,
        template='schedule/sessions_by_kind.html',
        context={
            'kind': kind,
            'sessions': sessions
        }
    )


def view_session(request, session_pk):
    """
    Renders all information available about a session.
    """
    session = get_object_or_404(models.Session, pk=session_pk, released=True)
    tags = list(session.tags.all())
    return TemplateResponse(
        request=request,
        context={
            'session': session,
            'tags': tags,
            'can_edit': utils.can_edit_session(request.user, session),
            'can_admin': request.user.has_perm('schedule.change_session'),
            'attending_possible': settings.SCHEDULE_ATTENDING_POSSIBLE,
            'is_attending': session.is_attending(request.user),
            'has_free_seats': session.has_free_seats(),
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
            'event': evt,
            'can_admin': request.user.has_perm('schedule.change_sideevent'),
        },
        template='schedule/sideevent.html'
    )


@login_required
def edit_session(request, session_pk):
    session = get_object_or_404(models.Session, pk=session_pk, released=True)
    if not utils.can_edit_session(request.user, session):
        return create_403()
    if session.end < now():
        form = forms.EditSessionCoverageForm
    else:
        form = forms.EditSessionForm
    if request.method == 'POST':
        form = form(instance=session, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Changes saved"))
            return HttpResponseRedirect(session.get_absolute_url())
    else:
        form = form(instance=session)
    return TemplateResponse(
        request=request,
        context={
            'form': form,
            'session': session
        },
        template='schedule/session_edit.html'
    )


@require_POST
@login_required
def attend_session(request, session_pk, attending):
    session = get_object_or_404(models.Session, pk=session_pk, released=True,
        kind__slug__in=settings.SCHEDULE_ATTENDING_POSSIBLE)
    try:
        if attending:
            session.attend(request.user)
            messages.success(request, _('You are now attending %(session_title)s.') % {
                'session_title': session.title,
            })
        elif not attending:
            session.leave(request.user)
            messages.success(request, _('You are not attending %(session_title)s anymore.') % {
                'session_title': session.title,
            })
        else:
            messages.error(request, _('Invalid or no action specified.'))
    except AttendingError as ae:
        messages.warning(request, ae.message)
    return HttpResponseRedirect(session.get_absolute_url())


@login_required
def list_user_attendances(request):
    """
    This view lists all the sessions to which the current user has indicated
    that they would like to attend.
    """
    sessions = request.user.profile.sessions_attending\
        .only('title', 'start', 'end')\
        .prefetch_related('location')\
        .order_by('start')\
        .all()
    return TemplateResponse(
        request=request,
        context={
            'sessions': sessions,
        },
        template='schedule/attending_sessions.html'
    )


def guidebook_export(request, kind):
    """
    A simple export of all sections as it can be used for importing into
    Guidebook.
    """
    if not request.user.has_perm('accounts_profile.export_guidebook'):
        raise PermissionDenied

    exporter_classes = {
        # 'sections': exporters.GuidebookExporterSections,
        'sessions': exporters.GuidebookExporterSessions,
        'speakers': exporters.GuidebookExporterSpeakers,
        'speaker-links': exporters.GuidebookExporterSpeakerLinks,
        # 'sponsors': exporters.GuidebookExporterSponsors,
    }

    exporter_class = exporter_classes.get(kind, None)
    if exporter_class is None:
        return HttpResponseBadRequest()

    cache_key = 'schedule:guidebook:%s' % kind
    data = cache.get(cache_key, None)
    if not data:
        data = exporter_class()().csv
        cache.set(cache_key, data)
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % kind
    return response

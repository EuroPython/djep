import urlparse

from django.views import generic as generic_views
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from braces.views import LoginRequiredMixin

from pyconde.conference.models import current_conference, SessionKind

from . import forms
from . import models
from . import settings


class NextRedirectMixin(object):
    """
    A simple mixin for checking for a next parameter for redirects.
    """
    redirect_param = 'next'

    def get_next_redirect(self):
        next = self.request.GET.get(self.redirect_param)
        if next is None:
            return None
        netloc = urlparse.urlparse(next)[1]
        if netloc is None or netloc == "" or netloc == self.request.get_host():
            return next
        return None


class TypedProposalFormMixin(object):
    """
    This mixin overrides the original get_form_class method in order to replace
    the default form with a type-specific form based on the type provided
    as view argument or already associated with the object to be processed.
    """
    def get_form_class(self):
        if settings.UNIFIED_SUBMISSION_FORM:
            return forms.ProposalSubmissionForm
        type_slug = None
        if getattr(self, 'object') and isinstance(self.object, models.Proposal):
            type_slug = self.object.kind.slug
        elif 'type' in self.kwargs:
            type_slug = self.kwargs['type']
        if type_slug:
            self.proposal_kind = SessionKind.current_objects.get(slug=type_slug)
            formcls_path = settings.TYPED_SUBMISSION_FORMS.get(type_slug)
            if formcls_path:
                mod_name, cls_name = formcls_path.rsplit('.', 1)
                mod = import_module(mod_name)
                form_cls = getattr(mod, cls_name)
                if form_cls:
                    return form_cls
        return forms.TypedSubmissionForm

    def get_form(self, form_class):
        form = super(TypedProposalFormMixin, self).get_form(form_class)
        if hasattr(self, 'proposal_kind'):
            setattr(form, 'kind_instance', self.proposal_kind)
        return form

    def get_template_names(self):
        """
        Also look for a template with the name proposals/%(type)s_proposal_form.html
        """
        proposed_names = super(TypedProposalFormMixin, self).get_template_names()
        if hasattr(self, 'proposal_kind'):
            base_name = proposed_names[0]
            base_dir, name = base_name.rsplit('/')
            proposed_names.insert(0, "proposals/{0}_proposal_form.html".format(self.proposal_kind.slug))
        return proposed_names


class SubmitProposalView(TypedProposalFormMixin, NextRedirectMixin, generic_views.CreateView):
    """
    Once registered a user can submit a proposal for the conference for a
    specific kind. This is only possible while the selected SessionKind
    accepts submissions.
    """
    model = models.Proposal

    # In this case we can't use LoginRequiredMixin since we override dispatch
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not len(SessionKind.current_objects.filter_open_kinds()):
            return TemplateResponse(request=request, template='proposals/closed.html', context={})
        if not settings.UNIFIED_SUBMISSION_FORM and 'type' not in kwargs:
            # If unified submission is disabled and no type has been specified
            # we have to show dummy page to tell the user what session kinds
            # now accept proposals
            session_kinds = []
            open_session_kinds = []
            for kind in SessionKind.current_objects.all():
                if kind.accepts_proposals():
                    open_session_kinds.append(kind)
                session_kinds.append(kind)
            if not open_session_kinds:
                return TemplateResponse(request=request, template='proposals/closed.html', context={})
            return TemplateResponse(request=request, template='proposals/submission_intro.html',
                context={
                    'session_kinds': session_kinds,
                    'open_kinds': open_session_kinds
                })
        return super(SubmitProposalView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next = self.get_next_redirect()
        if next:
            return next
        return super(SubmitProposalView, self).get_success_url()

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.speaker = self.request.user.speaker_profile
        # TODO: Filter out duplications between speaker and additional speakers
        obj.conference = current_conference()
        obj.save()
        self.object = obj
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())


class SingleProposalView(generic_views.DetailView):
    """
    Proposals can be viewed by everyone but provide some special links for
    administrators and people participating in this proposal.
    """
    model = models.Proposal

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # note: self.object is a Proposal
        # user is allowed to see Proposal if he is the author (speaker)
        # OR is he is a reviewer - both is checked in can_participate_in_review()
        from ..reviews.utils import can_participate_in_review
        if not can_participate_in_review(request.user, self.object):
            return TemplateResponse(request=request, template='proposals/denied.html', context={})
        return super(SingleProposalView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return self.model.objects.none()
        return self.model.objects.filter(conference=current_conference())

    def get_context_data(self, **kwargs):
        data = super(SingleProposalView, self).get_context_data(**kwargs)
        data['can_leave'] = self.request.user in [s.user for s in self.object.additional_speakers.all()]
        data['can_edit'] = self.request.user == self.object.speaker.user
        data['can_delete'] = self.request.user.is_staff or self.request.user == self.object.speaker.user
        return data


class PermissionCheckedUpdateView(generic_views.UpdateView, NextRedirectMixin):
    """
    Base update class that extends the UpdateView with an additional call
    of check_permissions.
    """
    def get_success_url(self):
        next = self.get_next_redirect()
        if next:
            return next
        return super(PermissionCheckedUpdateView, self).get_success_url()

    def get_context_data(self, *args, **kwargs):
        ctx = super(PermissionCheckedUpdateView, self).get_context_data(*args, **kwargs)
        ctx.update({
            'next': self.get_success_url()
            })
        return ctx

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        resp = self.check_permissions()
        if resp is not None:
            return resp
        return super(PermissionCheckedUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        resp = self.check_permissions()
        if resp is not None:
            return resp
        return super(PermissionCheckedUpdateView, self).post(request, *args, **kwargs)


class EditProposalView(LoginRequiredMixin, TypedProposalFormMixin, PermissionCheckedUpdateView):
    """
    The primary speaker can edit a proposal as long as the SessionKind
    still accepts proposals.
    """
    model = models.Proposal

    def form_valid(self, form):
        self.object = form.save()
        form.save_m2m()
        messages.success(self.request, _("Proposal successfully changed"))
        return HttpResponseRedirect(self.get_success_url())

    def check_permissions(self):
        """
        Only the primary speaker and staff members can edit a proposal.
        """
        user = self.request.user
        kind = self.object.kind
        if not kind.accepts_proposals():
            messages.error(self.request, _("You can no longer edit this proposal because the submission period has already ended."))
            return HttpResponseRedirect(self.object.get_absolute_url())
        if user != self.object.speaker.user and not user.is_staff:
            messages.error(self.request, _("You have to be the primary speaker mentioned in the proposal in order to edit it."))
            return HttpResponseRedirect(self.object.get_absolute_url())
        return None


class AbstractProposalAction(generic_views.DetailView, NextRedirectMixin):
    model = models.Proposal

    def check_permissions(self):
        pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        resp = self.check_permissions()
        if resp is not None:
            return resp
        return super(AbstractProposalAction, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        resp = self.check_permissions()
        if resp is not None:
            return resp
        resp = self.action()
        if resp is not None:
            return resp
        return HttpResponseRedirect(self.get_post_action_url())

    def get_context_data(self, *args, **kwargs):
        ctx = super(AbstractProposalAction, self).get_context_data(*args, **kwargs)
        ctx.update({
            'next': self.get_post_action_url()
            })
        return ctx

    def get_post_action_url(self):
        next = self.get_next_redirect()
        if next:
            return next
        return reverse('view_proposal', kwargs={'pk': self.object.pk})


class AbstractCancelProposalView(AbstractProposalAction):
    """
    During the submission and review period a proposal can be cancelled
    by the primary speaker. As soon as the review period is over
    and the proposal got accepted, an cancellation has to be communicated
    to the relevant staff member since this will involve rescheduling
    of other sessions.
    """
    template_name_suffix = '_cancel_confirm'
    model = models.Proposal

    def check_permissions(self):
        user = self.request.user
        kind = self.object.kind
        if not kind.accepts_proposals():
            messages.error(self.request, _("You can no longer cancel this proposal because the submission period has already ended."))
            return HttpResponseRedirect(self.object.get_absolute_url())
        if user != self.object.speaker.user:
            messages.error(self.request, _("You have to be the primary speaker mentioned in the proposal in order to cancel it."))
            return HttpResponseRedirect(self.object.get_absolute_url())
        return None

    def action(self):
        self.object.delete()
        messages.success(self.request, _("Proposal has been removed"))
        return None

    def get_post_action_url(self):
        next = self.get_next_redirect()
        if next:
            return next
        return reverse('my_proposals')


class CancelProposalView(LoginRequiredMixin, AbstractCancelProposalView):
    pass


class LeaveProposalView(LoginRequiredMixin, AbstractCancelProposalView):
    """
    A secondary speaker can decide not to actually take part in a session
    and therefor leave a proposal. This is an option that is exclusive
    to secondary speakers and is not available to the primary speaker.
    """
    template_name_suffix = "_leave_confirm"

    def check_permissions(self):
        user = self.request.user
        kind = self.object.kind
        if not kind.accepts_proposals():
            messages.error(self.request, _("You can no longer leave this proposal because the submission period has already ended."))
            return HttpResponseRedirect(self.object.get_absolute_url())
        if user not in [s.user for s in self.object.additional_speakers.all()]:
            messages.error(self.request, _("Only secondary speakers can leave a proposal"))
            return HttpResponseRedirect(self.object.get_absolute_url())
        return None

    def action(self):
        self.object.additional_speakers.remove(self.request.user.speaker_profile)
        messages.success(self.request, _("You were successfully removed as secondary speaker."))


class ListUserProposalsView(LoginRequiredMixin, generic_views.TemplateView):
    """
    A speaker can see and manage a list of proposals submitted by her or that
    include her as a secondary speaker.
    """
    template_name = 'proposals/proposal_list_mine.html'

    def get_context_data(self, **kwargs):
        this_speaker = self.request.user.speaker_profile
        ctx = super(ListUserProposalsView, self).get_context_data(**kwargs)
        ctx.update({
            'proposals': this_speaker.proposals
            .filter(conference=current_conference()).all(),
            'proposal_participations': this_speaker.proposal_participations
            .filter(conference=current_conference()).all()
        })
        return ctx


class IndexView(generic_views.View):
    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse('submit_proposal'))

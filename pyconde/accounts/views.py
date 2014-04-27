import json

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mass_mail
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic as generic_views

from userprofiles.contrib.emailverification.models import EmailVerification
from userprofiles.contrib.emailverification.views import EmailChangeView as BaseEmailChangeView
from userprofiles.contrib.profiles.views import ProfileChangeView as BaseProfileChangeView
from userprofiles.mixins import LoginRequiredMixin

from pyconde.conference.models import current_conference
from pyconde.reviews.models import Reviewer

from . import forms
from . import models
from .tasks import sendmail_task
from .utils import get_addressed_as, get_display_name


class AutocompleteUser(generic_views.View):
    """
    This view is used for instance within the proposals application to support
    the autocompletion widget in there.

    The current implementation matches users with the dipslay namee being
    equal to the given "term" parameter and returns their speaker pk as JSON
    object.

    TODO: Evaluation if this might be better placed somewhere within the
          speakers application.
    """

    def get_matching_users(self, term):
        """
        Returns a list of dicts containing a user's name ("label") and her
        speaker pk ("value").
        """
        result = []
        if not term:
            return result
        for profile in models.Profile.objects.filter(
                display_name__icontains=term):
            user = profile.user
            result.append({
                'label': u'{0} ({1})'.format(profile.display_name,
                    user.username),
                'value': user.speaker_profile.pk
            })
        return result

    def get(self, request):
        if 'term' not in request.GET:
            return HttpResponseBadRequest("You have to provide the GET parameter 'term'")
        term = request.GET['term']
        result = []
        if term and len(term) >= 2:
            result = self.get_matching_users(term)
        return HttpResponse(json.dumps(result), content_type='application/json')


class AutocompleteTags(generic_views.View):

    def get_matching_tags(self, term):
        if not term:
            return []
        data = list(models.Profile.tags.filter(name__icontains=term)
                                       .values_list('name', flat=True)
                                       .all()[:7])
        return data

    def get(self, request):
        if 'term' not in request.GET:
            return HttpResponseBadRequest("You have to provide the GET parameter 'term'")
        term = request.GET['term']
        result = []
        if term and len(term) >= 2:
            result = self.get_matching_tags(term)
        return HttpResponse(json.dumps(result), content_type='application/json')


class ProfileView(generic_views.TemplateView):
    """
    Displays a profile page for the given user. If the user also has a
    speaker_profile, also render the information given there.
    """

    template_name = 'userprofiles/profile_view.html'

    def get_context_data(self, uid):
        user = get_object_or_404(auth_models.User, pk=uid)
        speaker_profile = user.speaker_profile
        sessions = None
        profile = user.profile
        if speaker_profile:
            sessions = list(speaker_profile.sessions.all()) + list(speaker_profile.session_participations.all())
        return {
            'userobj': user,
            'speaker_profile': speaker_profile,
            'sessions': sessions,
            'profile': profile,
            'interests': profile.tags.order_by('name').all(),
        }


class LoginEmailRequestView(generic_views.FormView):
    """
    Requests an email address for the user currently trying to login. If the
    input is valid, continue the login process.
    """

    form_class = forms.LoginEmailRequestForm
    template_name = 'accounts/login-email-request.html'

    def form_valid(self, form):
        data = self.request.session[getattr(settings, 'SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')]
        backend = data['backend']
        user_pk = data['kwargs']['user']['pk']
        if form.cleaned_data['email']:
            user = auth_models.User.objects.get(pk=user_pk)
            EmailVerification.objects.create_new_verification(
                user, form.cleaned_data['email'])
        self.request.session['_email_passed_{0}'.format(user_pk)] = True
        return HttpResponseRedirect('/complete/{0}/'.format(backend))


class EmailChangeView(BaseEmailChangeView):
    form_class = forms.ChangeEmailForm


class ProfileChangeView(BaseProfileChangeView):

    def get_context_data(self, **kwargs):
        ctx = super(ProfileChangeView, self).get_context_data(**kwargs)
        review_state = None
        user = self.request.user
        if settings.REVIEWER_APPLICATION_OPEN:
            if not user.is_superuser:
                try:
                    review_state = user.reviewer_set.only('state').get().state
                except Reviewer.DoesNotExist:
                    pass
        ctx.update({
            'review_open': settings.REVIEWER_APPLICATION_OPEN,
            'review_state': review_state,
        })
        return ctx

    def form_invalid(self, form):
        messages.error(self.request, _('An error occurred while saving the form.'))
        return super(ProfileChangeView, self).form_invalid(form)


class ReviewerApplication(LoginRequiredMixin, generic_views.FormView):
    form_class = forms.ReviewerApplicationForm
    success_url = reverse_lazy('account_profile_change')
    template_name = 'accounts/reviewer_apply.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.REVIEWER_APPLICATION_OPEN:
            messages.error(request, _('The reviewer application is closed.'))
            return HttpResponseRedirect(self.get_success_url())
        if Reviewer.objects.filter(user=self.request.user).exists():
            messages.warning(request, _('You already applied as a reviewer.'))
            return HttpResponseRedirect(self.get_success_url())
        return super(ReviewerApplication, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reviewer_request = Reviewer.objects.create(user=self.request.user, conference=current_conference())
        reviewer_ct = ContentType.objects.get_for_model(Reviewer)
        perm = auth_models.Permission.objects.get(content_type_id=reviewer_ct.pk, codename='change_reviewer')
        mails = []
        subject = _('New reviewer application')
        from_email = settings.DEFAULT_FROM_EMAIL
        url = 'https://' if self.request.is_secure() else 'http://'
        url += self.request.get_host()
        url += reverse('admin:reviews_reviewer_change', args=(reviewer_request.pk,))
        data_dict = {
            'applicant_username': self.request.user.username,
            'applicant_display_name': get_display_name(self.request.user),
            'reviewer_list_url': url,
            'conference_title': current_conference().title,
        }
        for user in perm.user_set.all():
            data_dict['receiver'] = get_addressed_as(user)
            message = render_to_string('accounts/reviewer_application_mail.txt', data_dict)
            mails.append((subject, message, from_email, [user.email]))

        send_mass_mail(mails)
        return super(ReviewerApplication, self).form_valid(form)


class SendMailView(generic_views.FormView):

    form_class = forms.SendMailForm
    success_url = reverse_lazy('account_sendmail_done')
    template_name = 'accounts/sendmail_form.html'

    @method_decorator(permission_required('accounts.send_user_mails'))
    def dispatch(self, *args, **kwargs):
        return super(SendMailView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        domain = self.request.is_secure() and 'https://' or 'http://'
        domain += self.request.get_host() + '/'
        cd = form.cleaned_data
        sendmail_task.delay(cd['target'], cd['subject'], cd['text'], domain)
        return super(SendMailView, self).form_valid(form)

sendmail_view = SendMailView.as_view()


class SendMailDoneView(generic_views.TemplateView):

    template_name = 'accounts/sendmail_done.html'

    @method_decorator(permission_required('accounts.send_user_mails'))
    def dispatch(self, *args, **kwargs):
        return super(SendMailDoneView, self).dispatch(*args, **kwargs)

sendmaildone_view = SendMailDoneView.as_view()

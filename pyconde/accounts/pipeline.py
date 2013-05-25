"""
This holds extensions to social_auth's pipeline.
"""
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from userprofiles.contrib.emailverification.models import EmailVerification

from . import models


def create_profile(backend, details, response, user=None, **kwargs):
    """
    Creates a profile object for the new user.
    """
    assert user is not None
    if not models.Profile.objects.filter(user=user).count():
        models.Profile.objects.create(user=user).save()


def show_request_email_form(request, user, **kwargs):
    """
    If the user doesn't have an email associated and there is no email
    activation pending, ask the user to add an email to his/her account.
    """
    if user.email or EmailVerification.objects.get_pending(user):
        return
    session_key = '_email_passed_{0}'.format(user.pk)
    if session_key not in request.session:
        return HttpResponseRedirect(reverse('login-email-request'))
    else:
        del request.session[session_key]

from django.template import Library
from django.conf import settings

from .. import models
from .. import utils


register = Library()


@register.filter
def account_name(user):
    """
    Helper filter for rendering a user object independently of the
    unicode-version of that object.
    """
    return utils.get_account_name(user)


@register.filter
def display_name(user):
    return utils.get_display_name(user)


@register.filter
def addressed_as(user):
    return utils.get_addressed_as(user)


@register.inclusion_tag('accounts/tags/avatar.html')
def avatar(user, width=80):
    """
    Handles all avatar renderings in the frontend. If the user doesn't have
    an avatar attached to his profile, gravatar will be used if enabled in
    the settings.
    """
    if user is None:
        raise ValueError("A user or profile has to be passed as argument")
    profile = None
    email = None
    if isinstance(user, models.Profile):
        profile = user
        email = profile.user.email
    else:
        profile = user.profile
        email = user.email
    return {
        'profile': profile,
        'use_gravatar': getattr(settings, 'ACCOUNTS_FALLBACK_TO_GRAVATAR', False),
        'email': email,
        'width': width,
        'avatar_dimensions': '%sx%s' % (width, width),
    }

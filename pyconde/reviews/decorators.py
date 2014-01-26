from django.http import Http404

from django.utils.translation import ugettext as _
from django.contrib import messages

from pyconde.conference.models import current_conference
from pyconde.utils import create_403

from . import utils


def reviewer_required(func):
    """
    Requires that a user can actually create/update a review.
    """
    def _wrapper(request, *args, **kwargs):
        if not utils.can_review_proposal(request.user):
            return create_403(request, _("You have to be a reviewer in order to access this page."))
        return func(request, *args, **kwargs)
    return _wrapper


def reviewer_or_staff_required(func):
    def _wrapper(request, *args, **kwargs):
        if not (utils.can_review_proposal(request.user) or request.user.is_staff):
            return create_403(request, _("You have to be a reviewer or staff member in order to access this page."))
        return func(request, *args, **kwargs)
    return _wrapper


def reviews_active_required(func):
    def _wrapper(request, *args, **kwargs):
        if not current_conference().get_reviews_active():
            if not request.user.is_staff:
                raise Http404()
            messages.warning(request, _("The review period has ended. Only staff members may access this page."))
        return func(request, *args, **kwargs)
    return _wrapper

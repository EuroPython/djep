from django.http import HttpResponseForbidden
from django.http import Http404

from pyconde.conference.models import current_conference

from . import utils


def reviewer_required(func):
    """
    Requires that a user can actually create/update a review.
    """
    def _wrapper(request, *args, **kwargs):
        if not utils.can_review_proposal(request.user):
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return _wrapper


def reviews_active_required(func):
    def _wrapper(request, *args, **kwargs):
        if not current_conference().get_reviews_active():
            raise Http404()
        return func(request, *args, **kwargs)
    return _wrapper

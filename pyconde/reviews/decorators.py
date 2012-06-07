from django.http import HttpResponseForbidden

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

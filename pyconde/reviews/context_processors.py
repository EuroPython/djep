from . import utils


def review_roles(request):
    can_review = False
    if hasattr(request, 'user'):
        can_review = utils.can_review_proposal(request.user)
    return {
        'is_reviewer': can_review
        }

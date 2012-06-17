from . import utils


def review_roles(request):
    return {
        'is_reviewer': utils.can_review_proposal(request.user)
        }

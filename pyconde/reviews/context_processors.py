from . import utils


def review_roles(request):
    can_review = False
    can_see_proposal_author = False
    if hasattr(request, 'user'):
        can_review = utils.can_review_proposal(request.user)
        can_see_proposal_author = utils.can_see_proposal_author(request.user)
    return {
        'is_reviewer': can_review,
        'can_see_proposal_author': can_see_proposal_author,
    }

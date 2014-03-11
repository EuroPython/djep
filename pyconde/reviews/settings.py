from django.conf import settings


ENABLE_COMMENT_NOTIFICATIONS = getattr(settings, 'REVIEWS_ENABLE_COMMENT_NOTIFICATIONS', True)
ENABLE_PROPOSAL_UPDATE_NOTIFICATIONS = getattr(settings, 'REVIEW_ENABLE_PROPOSAL_UPDATE_NOTIFICATIONS', True)

PROPOSAL_UPDATE_FORMS = getattr(settings, 'REVIEWS_PROPOSAL_UPDATE_FORMS', {
    'talk': 'pyconde.reviews.forms.UpdateTalkProposalForm',
    'training': 'pyconde.reviews.forms.UpdateTrainingProposalForm',
    })

RATING_MAPPING = getattr(settings, 'REVIEW_RATING_MAPPING', {
    '-0': -0.5,
    '+0': +0.5,
    '+1': +1,
    '-1': -1,
    })

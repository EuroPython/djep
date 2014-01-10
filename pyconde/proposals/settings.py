from django.conf import settings as global_settings


SUPPORT_ADDITIONAL_SPEAKERS = getattr(global_settings,
    'PROPOSALS_SUPPORT_ADDITIONAL_SPEAKERS', True)
UNIFIED_SUBMISSION_FORM = getattr(global_settings,
    'PROPOSALS_UNIFIED_SUBMISSION_FORM', False)
TYPED_SUBMISSION_FORMS = getattr(global_settings,
    'PROPOSALS_TYPED_SUBMISSION_FORMS', {})

# This setting defines the language that should be pre-selected in the
# proposal submission form.
DEFAULT_LANGUAGE = getattr(global_settings,
    'PROPOSALS_DEFAULT_LANGUAGE', 'en')

from django.conf import settings as global_settings


SUPPORT_ADDITIONAL_SPEAKERS = getattr(global_settings,
    'PROPOSALS_SUPPORT_ADDITIONAL_SPEAKERS', True)

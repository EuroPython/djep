from django.conf import settings


def less_settings(request):
    return {
        'use_dynamic_less_in_debug': getattr(settings, 'LESS_USE_DYNAMIC_IN_DEBUG', True)
    }

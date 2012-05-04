from . import models


def current_conference(request):
    return {
        'current_conference': models.current_conference()
    }

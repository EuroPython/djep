# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from . import models


def current_conference(request):
    return {
        'current_conference': models.current_conference(),
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
    }

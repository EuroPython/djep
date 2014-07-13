# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from ..conference.models import current_conference


def during_conference(value):
    """
    The username has to be at max. 15 characters and not start with a "@"
    """
    if value:
        cc = current_conference()
        if not cc.start_date <= value <= cc.end_date:
            raise ValidationError(
                _('The ticket validation date is outside the conference time'))

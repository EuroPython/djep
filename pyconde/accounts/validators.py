# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from PIL import Image


AVATAR_MIN_DIMENSION = getattr(settings, 'AVATAR_MIN_DIMENSION', None)
AVATAR_MAX_DIMENSION = getattr(settings, 'AVATAR_MAX_DIMENSION', None)


def twitter_username(value):
    """
    The username has to be at max. 15 characters and not start with a "@"
    """
    if len(value) > 15:
        raise ValidationError(
            _("Twitter usernames have only 15 characters or less"))
    if value.startswith("@"):
        raise ValidationError(
            _("Please omit the @ at the start of the twitter username"))


def avatar_dimension(value):
    if value and (AVATAR_MIN_DIMENSION or AVATAR_MAX_DIMENSION):
        img = Image.open(value)
        size = img.size
        if AVATAR_MIN_DIMENSION and size < AVATAR_MIN_DIMENSION:
            raise ValidationError(_(
                'Minimum avatar size is %(min_w)dx%(min_h)d px. Yours is %(yours_w)dx%(yours_h)d px') % {
                    'min_w': AVATAR_MIN_DIMENSION[0],
                    'min_h': AVATAR_MIN_DIMENSION[1],
                    'yours_w': size[0],
                    'yours_h': size[1]})
        if AVATAR_MAX_DIMENSION and size > AVATAR_MAX_DIMENSION:
            raise ValidationError(_(
                'Maximum avatar size is %(max_w)dx%(max_h)d px. Yours is %(yours_w)dx%(yours_h)d px') % {
                    'max_w': AVATAR_MAX_DIMENSION[0],
                    'max_h': AVATAR_MAX_DIMENSION[1],
                    'yours_w': size[0],
                    'yours_h': size[1]})
    return value

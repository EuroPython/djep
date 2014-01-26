# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from os.path import splitext

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
        try:
            size = (value.width, value.height)
        except Exception:
            raise ValidationError(_("It was not possible to determine the "
                                    "avatar dimensions."))
        if AVATAR_MIN_DIMENSION and (size[0] < AVATAR_MIN_DIMENSION[0] or
                                     size[1] < AVATAR_MIN_DIMENSION[1]):
            raise ValidationError(_(
                'Minimum avatar size is %(min_w)dx%(min_h)d px. Yours is %(yours_w)dx%(yours_h)d px') % {
                    'min_w': AVATAR_MIN_DIMENSION[0],
                    'min_h': AVATAR_MIN_DIMENSION[1],
                    'yours_w': size[0],
                    'yours_h': size[1]})
        if AVATAR_MAX_DIMENSION and (size[0] > AVATAR_MAX_DIMENSION[0] or
                                     size[1] > AVATAR_MAX_DIMENSION[1]):
            raise ValidationError(_(
                'Maximum avatar size is %(max_w)dx%(max_h)d px. Yours is %(yours_w)dx%(yours_h)d px') % {
                    'max_w': AVATAR_MAX_DIMENSION[0],
                    'max_h': AVATAR_MAX_DIMENSION[1],
                    'yours_w': size[0],
                    'yours_h': size[1]})
    return value


def avatar_format(value):
    """
    Checks the actual image file if it is of a supported format
    (JPG, PNG or GIF).
    """
    error_msg = _("Your avatar has to be either a PNG, JPEG or GIF file.")
    if value is None or value == "":
        return
    image = None
    try:
        image = Image.open(value)
    except Exception:
        raise ValidationError(error_msg)

    if image.format not in ('PNG', 'JPEG', 'GIF'):
        raise ValidationError(error_msg)

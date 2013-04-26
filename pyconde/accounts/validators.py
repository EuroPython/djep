from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def twitter_username(value):
    """
    The username has to be at max. 15 characters and not start with a "@"
    """
    if len(value) > 15:
        raise ValidationError(
            _("Twitter usernames only have 15 or less characters"))
    if value.startswith("@"):
        raise ValidationError(
            _("Please omit the @ at the start of the twitter username"))

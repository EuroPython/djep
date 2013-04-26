from django.template import Library


register = Library()


@register.filter
def account_name(user):
    """
    Helper filter for rendering a user object independently of the
    unicode-version of that object.
    """
    if user is None:
        return None
    if user.first_name and user.last_name and user.first_name.lstrip() and user.last_name.lstrip():
        return u'{0} {1}'.format(user.first_name, user.last_name)
    return user.username

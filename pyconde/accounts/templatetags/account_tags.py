from django.template import Library


register = Library()


@register.filter
def account_name(user):
    if user.first_name and user.last_name:
        return u'{0} {1}'.format(user.first_name, user.last_name)
    return user.username
def get_account_name(user):
    if user is None:
        return None
    if user.first_name and user.last_name and user.first_name.lstrip() and user.last_name.lstrip():
        return u'{0} {1}'.format(user.first_name, user.last_name)
    return user.username


def get_display_name(user):
    if user is None:
        return None
    profile = user.get_profile()
    if profile.display_name:
        return profile.display_name
    return user.username


def get_addressed_as(user):
    if user is None:
        return None
    profile = user.get_profile()
    if profile.addressed_as:
        return profile.addressed_as
    return get_display_name(user)

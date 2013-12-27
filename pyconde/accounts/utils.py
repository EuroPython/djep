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

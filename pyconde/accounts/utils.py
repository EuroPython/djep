def get_account_name(user):
    if user is None:
        return None
    if user.first_name and user.last_name and user.first_name.lstrip() and user.last_name.lstrip():
        return u'{0} {1}'.format(user.first_name, user.last_name)
    return user.username

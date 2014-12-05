GROUP_EDIT_EVENTS = 'Contributors'


def user_in_group_or_super(user):
    """Checks that a user is in a particular group or is a superuser
    :param user: django User
    :return: True if the user is in the given group or has superuser status else False
    """
    if user.is_superuser:
        return True
    elif user.groups.filter(name=GROUP_EDIT_EVENTS).exists():
        return True
    return False

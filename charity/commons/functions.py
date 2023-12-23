def user_should_be_volunteer(user):
    return hasattr(user, 'volunteer_profile') and user.volunteer_profile is not None

def user_should_be_superuser(user):
    return user.is_superuser
from django.conf import settings
from django.contrib.auth.hashers import check_password

from fei.models import AppUser


class SettingsBackend:
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. It is used for authentication in development.
    DO NOT USE IN PRODUCTION.
    """

    def authenticate(self, request, username=None, password=None):
        login_valid = username in settings.ADMIN_LOGIN
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = AppUser.objects.get(username=username)
                user.is_active = True
                user.save()
            except AppUser.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = AppUser(username=username)
                user.is_active = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return AppUser.objects.get(pk=user_id)
        except AppUser.DoesNotExist:
            return None
# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class CustomBackend(ModelBackend):
    """Custom authentication backend"""

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                'password crect'
                try:
                    return User.objects.get(username=username)
                except User.DoesNotExist:
                    return User.objects.create_user(user)
            else:
                'password increct'
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

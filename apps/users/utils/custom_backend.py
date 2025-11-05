from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class MultiFieldBackend(ModelBackend):
    """
    Authentication backend that allows login with email, username, or phone_number
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email, username, or phone_number
            user = User.objects.get(
                Q(email__iexact=username) |
                Q(username__iexact=username) |
                Q(phone_number=username)
            )

            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            pass
        return None

from django.contrib.auth.backends import ModelBackend
from .models import MMDEUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (username or kwargs.get('email') or '').strip().lower()
        if not email or not password:
            return None
        try:
            user = MMDEUser.objects.get(email__iexact=email)
            if user.check_password(password) and user.is_active:
                return user
        except MMDEUser.DoesNotExist:
            return None

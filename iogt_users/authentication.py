from django.conf import settings
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class IogtBasicAuthentication(BasicAuthentication):
    def authenticate(self, request):
        user = super().authenticate(request)
        if user and user[0].id != settings.RAPIDPRO_BOT_USER_ID:
            raise AuthenticationFailed('User not allowed.')
        return user

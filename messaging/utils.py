from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


def get_auth_tokens():
    users = User.objects.filter(groups__name=settings.RAPIDPRO_BOT_GROUP_NAME)

    return {
        user.username: f"Bearer {RefreshToken.for_user(user).access_token}"
        for user in users
    }


def is_chatbot(user) -> bool:
    try:
        return user.groups.filter(name=settings.RAPIDPRO_BOT_GROUP_NAME).exists()
    except Exception:
        return False

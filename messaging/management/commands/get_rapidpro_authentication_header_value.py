import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    This command prints the Authorization Header Value for RapidPro
    """

    def handle(self, *args, **options):
        auth_str = f'{settings.RAPIDPRO_BOT_USER_USERNAME}:{settings.RAPIDPRO_BOT_USER_PASSWORD}'
        message_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_auth_str = f'Basic {base64_bytes.decode("ascii")}'

        self.stdout.write(self.style.SUCCESS(base64_auth_str))
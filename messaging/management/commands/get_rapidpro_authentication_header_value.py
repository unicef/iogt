from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from messaging.utils import get_auth_tokens


class Command(BaseCommand):
    """
    Print the authorization header for each chatbot user
    """
    def handle(self, *args, **options):
        tokens = get_auth_tokens()

        for username, token in tokens.items():
            self.stdout.write(self.style.SUCCESS(f'{username}: {token}'))

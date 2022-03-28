from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    This command prints the Authorization Header Value for RapidPro
    """

    def handle(self, *args, **options):
        tokens = User.get_rapidpro_bot_auth_tokens()
        for username, token in tokens.items():
            self.stdout.write(self.style.SUCCESS(f'{username}: {token}'))

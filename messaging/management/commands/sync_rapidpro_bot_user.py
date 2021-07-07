from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    This command creates or updates the RapidPro Bot user that is used for
    integration with RapidPro Server. Make sure that the authorization
    headers in RapidPro settings match the username and password mentioned
    in the settings file.
    """

    def handle(self, *args, **options):
        user = User.objects.filter(username=settings.RAPIDPRO_BOT_USER_USERNAME).first()
        first_name = 'RapidPro'
        last_name = 'Bot'
        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.set_password(settings.RAPIDPRO_BOT_USER_PASSWORD)
            user.save(update_fields=['display_name', 'password'])
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User updated successfully. ID: {user.pk}'))
        else:
            bot_user = User.objects.create_user(
                username=settings.RAPIDPRO_BOT_USER_USERNAME, password=settings.RAPIDPRO_BOT_USER_PASSWORD,
                first_name=first_name, last_name=last_name)
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User created successfully. ID: {bot_user.pk}'))

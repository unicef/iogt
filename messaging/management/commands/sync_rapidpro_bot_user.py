from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    This command creates or updates the RapidPro Bot user that is used for
    integration with RapidPro Server.
    """

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=settings.RAPIDPRO_BOT_USER_USERNAME, defaults={'first_name': 'RapidPro', 'last_name': 'Bot'})
        group, created = Group.objects.get_or_create(name=settings.RAPIDPRO_BOT_GROUP_NAME)
        user.groups.add(group)

        if created:
            user.set_password(User.objects.make_random_password())
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User created successfully. ID: {user.pk}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User updated successfully. ID: {user.pk}'))

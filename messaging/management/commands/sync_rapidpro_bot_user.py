from uuid import uuid4

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

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default=uuid4(),
            help='This username will be used to create or update rapidpro chatbot user.',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        user, created = User.objects.get_or_create(
            username=username, defaults={'first_name': 'RapidPro', 'last_name': 'Bot'})
        group, __ = Group.objects.get_or_create(name=settings.RAPIDPRO_BOT_GROUP_NAME)
        user.groups.add(group)

        if created:
            user.set_password(User.objects.make_random_password())
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User created successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'RapidPro Bot User updated successfully.'))

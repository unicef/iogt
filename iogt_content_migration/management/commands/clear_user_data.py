from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_user_model().objects.all().delete()
        self.stdout.write('User data cleared.')

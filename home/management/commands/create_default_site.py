from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        _, created = Site.objects.update_or_create(pk=settings.SITE_ID, defaults={
            'domain': 'localhost:8000',
            'name': 'default'
        })
        self.stdout.write(self.style.SUCCESS(f'Site object {"created" if created else "updated"}'))

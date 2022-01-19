from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site as DjangoSite
from django.core.management.base import BaseCommand
from wagtail.core.models import Site as WagtailSite

from home.models import HomePage

User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            help='The domain on which the website is deployed'
        )

    def handle(self, *args, **options):
        domain = options.get('domain') or 'localhost:8000'

        __, created = DjangoSite.objects.update_or_create(pk=settings.SITE_ID, defaults={
            'domain': domain,
            'name': 'default'
        })
        self.stdout.write(self.style.SUCCESS(f'Django Site object {"created" if created else "updated"}'))
        __, created = WagtailSite.objects.update_or_create(is_default_site=True, defaults={
            'hostname': domain,
            'site_name': 'default',
            'root_page': HomePage.objects.all().order_by('id').first()
        })
        self.stdout.write(self.style.SUCCESS(f'Wagtail Site object {"created" if created else "updated"}'))

from pathlib import Path

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from home.models import SiteSettings


class Command(BaseCommand):
    def handle(self, *args, **options):
        self._load_logo_and_favicon()

        self.stdout.write(self.style.SUCCESS('Loaded successfully.'))

    def _open_file(self, path):
        try:
            return open(path, 'rb')
        except:
            self.stdout.write(self.style.WARNING(f'File not found: {path}.'))

    def _load_logo_and_favicon(self):
        file = ImageFile(self._open_file(Path(settings.BASE_DIR) / 'iogt/static/images/logo.png'), name='logo.png')
        logo = Image.objects.create(title='Logo', file=file)

        file = ImageFile(self._open_file(Path(settings.BASE_DIR) / 'iogt/static/images/favicon.png'), name='favicon.png')
        favicon = Image.objects.create(title='Favicon', file=file)

        site_settings = SiteSettings.get_for_default_site()
        site_settings.logo = logo
        site_settings.favicon = favicon
        site_settings.save(update_fields=['logo', 'favicon'])

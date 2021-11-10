from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from translation_manager.manager import Manager

from iogt.patch import patch_store_to_db


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(_('Reloading translations...'))
        patch_store_to_db()

        manager = Manager()
        manager.load_data_from_po()
        self.stdout.write(_('The translations have been loaded successfully!'))

        for language, language_name in settings.LANGUAGES:
            manager.update_po_from_db(lang=language)
        self.stdout.write(_('The translations have been published successfully!'))

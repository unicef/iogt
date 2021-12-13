from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from translation_manager.manager import Manager

from iogt.patch import patch_store_to_db


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(_('Loading translations...'))
        patch_store_to_db()

        manager = Manager()
        manager.load_data_from_po()
        self.stdout.write(_('The translations have been loaded successfully!'))

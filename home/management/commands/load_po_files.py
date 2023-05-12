from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from home.translation_manager.manager import IogtTranslationManager as Manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(_('Loading translations...'))
        Manager().load_data_from_po()
        self.stdout.write(_('The translations have been loaded successfully!'))

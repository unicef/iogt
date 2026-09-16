import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from common.translation_utils.make_pos import make_pos_run
from common.translation_utils.make_testing_po import make_testing_po_run
from common.translation_utils.update_status import update_status_run


#This management function runs a series of functions related to the translation process, for detailed information see common/translation_utils/README

class Command(BaseCommand):
    help = 'Updates translation translation tracking sheets and PO files'

    def handle(self, *args, **options):
        #Extracts message content from codebase and stores in locale/xy/LC_MESSAGES
        call_command('makemessages', '-l' 'xy', '-d django', '--keep-pot')
        call_command('makemessages', '-l' 'xy', '-d djangojs', '--keep-pot')

        # Processes messages from locale/xy/LC_MESSAGES, looks through ‘translation_status.csv’ and ‘translations.csv’ 
        # and creates an up to date log of translation which are present and their status
        update_status_run()

        # Uses the excel files to create the necessary PO files, stores them in locale. 
        # Also creates a file ‘translatable_strings’ with translations that we need but don’t have
        make_testing_po_run()
        make_pos_run()

        os.remove('locale/django.pot')
        os.remove('locale/djangojs.pot')

        # Compile PO files into binary MO files for gettext runtime
        self.stdout.write('Compiling messages to MO files...')
        call_command('compilemessages')

        # Load PO translations into TranslationEntry database table
        self.stdout.write('Loading translations into database...')
        call_command('load_po_files')

        # Clear translation cache maps and Wagtail page cache
        from django.core.cache import cache
        from django.conf import settings
        from wagtailcache.cache import clear_cache
        for lang, _ in settings.LANGUAGES:
            cache.delete(f'{lang}_translation_map')
        clear_cache()
        self.stdout.write(self.style.SUCCESS('Translation tracking and update complete.'))

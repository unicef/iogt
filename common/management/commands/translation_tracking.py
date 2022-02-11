from django.core.management.base import BaseCommand
from django.core.management import call_command
from common.translation_utils.update_status import update_status_run
from common.translation_utils.make_testing_po import make_testing_po_run
from common.translation_utils.make_pos import make_pos_run
import polib
import csv
import copy
import os

#This management function runs a series of functions related to the translation process, for detailed information see common/translation_utils/README

class Command(BaseCommand):
    help = 'Updates translation translation tracking sheets and PO files'

    def handle(self, *args, **options):
        #Extracts message content from codebase and stores in locale/xy/LC_MESSAGES
        call_command('makemessages', '-l' 'xy', '-d django')
        call_command('makemessages', '-l' 'xy', '-d djangojs')

        # Processes messages from locale/xy/LC_MESSAGES, looks through ‘translation_status.csv’ and ‘translations.csv’ 
        # and creates an up to date log of translation which are present and their status
        update_status_run()

        # Uses the excel files to create the necessary PO files, stores them in locale. 
        # Also creates a file ‘translatable_strings’ with translations that we need but don’t have
        make_testing_po_run()
        make_pos_run()
        

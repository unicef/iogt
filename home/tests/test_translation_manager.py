from pathlib import Path

from django.test import TestCase, override_settings
from translation_manager.models import TranslationEntry

from home.translation_manager.manager import IogtTranslationManager

class LoadTranslationsFromFileTests(TestCase):

    LANGUAGES = [ ('es', 'Spanish') ]
    LOCALE_PATHS = [ Path(__file__).parent / 'locale_test' ]

    def setUp(self):
        self.manager = IogtTranslationManager()


    @override_settings(LOCALE_PATHS=LOCALE_PATHS, LANGUAGES=LANGUAGES)
    def test_existing_translated_entry_is_preserved(self):
        self.create_entry('test_case_1', 'test_case_1_translation_existing')

        self.manager.load_data_from_po()

        entry = TranslationEntry.objects.get(original='test_case_1')
        self.assertEqual(entry.translation, 'test_case_1_translation_existing')
        self.assertTrue(entry.is_published)


    @override_settings(LOCALE_PATHS=LOCALE_PATHS, LANGUAGES=LANGUAGES)
    def test_untranslated_entry_is_replaced_with_translated_entry(self):
        self.create_entry('test_case_2', '')

        self.manager.load_data_from_po()

        entry = TranslationEntry.objects.get(original='test_case_2')
        self.assertEqual(entry.translation, 'test_case_2_translation_update')
        self.assertTrue(entry.is_published)


    @override_settings(LOCALE_PATHS=LOCALE_PATHS, LANGUAGES=LANGUAGES)
    def test_new_entry_created_from_file(self):
        self.manager.load_data_from_po()

        entry = TranslationEntry.objects.get(original='test_case_3.1')
        self.assertEqual(entry.translation, 'test_case_3.1_translation')
        self.assertEqual(entry.language, 'es')
        self.assertEqual(entry.domain, 'django')
        self.assertEqual(entry.locale_path, 'home/tests/locale_test')
        self.assertEqual(entry.locale_parent_dir, 'tests')
        self.assertTrue(entry.is_published)

        entry = TranslationEntry.objects.get(original='test_case_3.2')
        self.assertEqual(entry.translation, '')
        self.assertTrue(entry.is_published)


    @override_settings(LOCALE_PATHS=LOCALE_PATHS, LANGUAGES=LANGUAGES)
    def test_existing_untranslated_entry_is_preserved_if_no_translation_in_file(self):
        self.create_entry('test_case_4', '')

        self.manager.load_data_from_po()

        entry = TranslationEntry.objects.get(original='test_case_4')
        self.assertEqual(entry.translation, '')
        self.assertTrue(entry.is_published)


    def create_entry(self, original, translation):
        TranslationEntry(
            original=original,
            language='es',
            translation=translation,
            domain='django',
            locale_path='home/tests/locale_test',
            locale_parent_dir='tests',
            is_published=True
        ).save()

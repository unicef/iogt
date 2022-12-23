from django.test import TestCase
from django.http import HttpRequest
from translation_manager.models import TranslationEntry
from wagtail.core.models import Site
from wagtail_localize.operations import TranslationCreator

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SurveyFactory, LocaleFactory
from wagtail_factories import SiteFactory
from bs4 import BeautifulSoup

class LimitPageChooserHookTests(TestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

        self.article01 = ArticleFactory(parent=self.home_page)
        self.section01 = SectionFactory(parent=self.home_page)
        self.section02 = SectionFactory(parent=self.section01)
        self.article02 = ArticleFactory(parent=self.section01)

    def test_start_from_section_when_current_page_is_section(self):
        request = HttpRequest()
        request.path = '/admin/choose-page/'
        request.META['HTTP_REFERER'] = f'https://example.com/admin/pages/{self.section01.id}/edit/'
        pages = self.home_page.get_children()

        pages = limit_page_chooser(pages, request)

        self.assertEqual([i for i in pages.values_list('id', flat=True)], [self.section02.id, self.article02.id])

    def test_start_from_section_when_parent_page_is_section(self):
        request = HttpRequest()
        request.path = f'/admin/choose-page/{self.section01.id}/'
        pages = self.home_page.get_children()

        pages = limit_page_chooser(pages, request)

        self.assertEqual([i for i in pages.values_list('id', flat=True)], [self.section02.id, self.article02.id])

    def test_do_not_change_queryset_when_current_page_is_not_a_section(self):
        request = HttpRequest()
        request.path = '/admin/choose-page/'
        request.META['HTTP_REFERER'] = f'https://example.com/admin/pages/{self.home_page.id}/edit/'
        pages_before = self.home_page.get_children()

        pages_after = limit_page_chooser(pages_before, request)

        self.assertEqual(pages_after, pages_before)

    def test_do_not_change_queryset_when_parent_page_is_not_a_section(self):
        request = HttpRequest()
        request.path = f'/admin/choose-page/{self.home_page.id}/'
        pages_before = self.home_page.get_children()

        pages_after = limit_page_chooser(pages_before, request)

        self.assertEqual(pages_after, pages_before)


class SurveyTranslationTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.en_home_page = self.site.root_page
        self.en_survey = SurveyFactory(parent=self.en_home_page)

    def test_survey_translation_of_english_language(self):
        response = self.client.get(self.en_survey.url)
        soup = BeautifulSoup(response.content)
        submit_button_text = soup.find("button", {"type": "submit"}).text.strip()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(submit_button_text, 'Submit')

    def test_survey_translation_of_arabic_language(self):
        ar_locale = LocaleFactory(language_code='ar')
        ar_translation_creator = TranslationCreator(user=None, target_locales=[ar_locale])
        ar_translation_creator.create_translations(self.en_survey)
        ar_survey = self.en_survey.get_translation(ar_locale)
        TranslationEntry.objects.create(
            original="Submit",
            translation="إرسال",
            language=ar_locale.language_code)

        response = self.client.get(ar_survey.url)
        soup = BeautifulSoup(response.content)
        submit_button_text = soup.find("button", {"type": "submit"}).text.strip()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(submit_button_text, "إرسال")

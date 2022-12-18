from django.test import TestCase
from django.http import HttpRequest
from translation_manager.models import TranslationEntry
from wagtail.core.models import Site
from wagtail_localize.operations import TranslationCreator

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, MediaFactory, LocaleFactory
from wagtail_factories import SiteFactory


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


class MediaTranslationTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.bn_locale = LocaleFactory(language_code='bn')
        bn_translation_creator = TranslationCreator(user=None, target_locales=[self.bn_locale])
        self.en_home_page = self.site.root_page
        bn_translation_creator.create_translations(self.en_home_page)
        self.bn_home_page = self.en_home_page.get_translation(self.bn_locale)
        self.en_article = ArticleFactory(
            parent=self.en_home_page,
            body__0__media=MediaFactory(type='video'),
            body__1__media=MediaFactory(type='audio'),
        )
        bn_translation_creator.create_translations(self.en_article)
        self.bn_article = self.en_article.get_translation(self.bn_locale)

    def test_media_block_translation_of_english_language(self):
        response = self.client.get(self.en_article.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"If you cannot view the above video, you can instead <a href='{self.en_article.body[0].value.url}' download>download it</a>.")
        self.assertContains(response, f"If you cannot listen to the above audio, you can instead <a href='{self.en_article.body[1].value.url}' download>download it</a>.")

    def test_media_block_translation_of_bengali_language(self):
        TranslationEntry.objects.create(
            original="If you cannot view the above video, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের ভিডিও দেখা না গেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=self.bn_locale.language_code)
        TranslationEntry.objects.create(
            original="If you cannot listen to the above audio, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের অডিও শুনতে না পেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=self.bn_locale.language_code)

        response = self.client.get(self.bn_article.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"উপরের ভিডিও দেখা না গেলে <a href='{self.bn_article.body[0].value.url}' download> এর পরিবর্তে এটা </a> ডাউনলোড করুন")
        self.assertContains(response, f"উপরের অডিও শুনতে না পেলে <a href='{self.bn_article.body[1].value.url}' download> এর পরিবর্তে এটা </a> ডাউনলোড করুন")

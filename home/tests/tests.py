from django.test import TestCase
from django.http import HttpRequest
from translation_manager.models import TranslationEntry
from wagtail.core.models import Site
from wagtail_localize.operations import TranslationCreator

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, MediaFactory, LocaleFactory
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


class MediaTranslationTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.en_home_page = self.site.root_page
        self.en_article = ArticleFactory(
            parent=self.en_home_page,
            body__0__media=MediaFactory(type='video'),
            body__1__media=MediaFactory(type='audio'),
        )

    def test_media_block_translation_of_english_language(self):
        response = self.client.get(self.en_article.url)
        soup = BeautifulSoup(response.content)
        video_text = soup.find("p", {"class": "article__content--video"}).text.strip()
        video_link = soup.find("p", {"class": "article__content--video"}).find("a").get("href")
        audio_text = soup.find("p", {"class": "article__content--audio"}).text.strip()
        audio_link = soup.find("p", {"class": "article__content--audio"}).find("a").get("href")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(video_text, 'If you cannot view the above video, you can instead download it.')
        self.assertEqual(video_link, self.en_article.body[0].value.url)
        self.assertEqual(audio_text, 'If you cannot listen to the above audio, you can instead download it.')
        self.assertEqual(audio_link, self.en_article.body[1].value.url)

    def test_media_block_translation_of_bengali_language(self):
        bn_locale = LocaleFactory(language_code='bn')
        bn_translation_creator = TranslationCreator(user=None, target_locales=[bn_locale])
        bn_translation_creator.create_translations(self.en_article)
        bn_article = self.en_article.get_translation(bn_locale)

        TranslationEntry.objects.create(
            original="If you cannot view the above video, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের ভিডিও দেখা না গেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=bn_locale.language_code)
        TranslationEntry.objects.create(
            original="If you cannot listen to the above audio, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের অডিও শুনতে না পেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=bn_locale.language_code)

        response = self.client.get(bn_article.url)
        soup = BeautifulSoup(response.content)
        video_text = soup.find("p", {"class": "article__content--video"}).text.strip()
        video_link = soup.find("p", {"class": "article__content--video"}).find("a").get("href")
        audio_text = soup.find("p", {"class": "article__content--audio"}).text.strip()
        audio_link = soup.find("p", {"class": "article__content--audio"}).find("a").get("href")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(video_text, 'উপরের ভিডিও দেখা না গেলে  এর পরিবর্তে এটা  ডাউনলোড করুন')
        self.assertEqual(video_link, self.en_article.body[0].value.url)
        self.assertEqual(audio_text, 'উপরের অডিও শুনতে না পেলে  এর পরিবর্তে এটা  ডাউনলোড করুন')
        self.assertEqual(audio_link, self.en_article.body[1].value.url)

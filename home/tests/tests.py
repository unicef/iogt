from bs4 import BeautifulSoup
from django.test import TestCase, override_settings
from django.http import HttpRequest
from translation_manager.models import TranslationEntry
from wagtail.core.models import Site
from wagtail_factories import SiteFactory, PageFactory
from wagtail_localize.operations import TranslationCreator

from home.wagtail_hooks import limit_page_chooser
from home.factories import (
    SectionFactory,
    ArticleFactory,
    HomePageFactory,
    MediaFactory,
    LocaleFactory,
    SiteSettingsFactory
)


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
        root_page = PageFactory(parent=None)
        en_home_page = HomePageFactory(parent=root_page)
        SiteFactory(hostname='testserver', port=80, root_page=en_home_page)
        self.en_article = ArticleFactory(
            parent=en_home_page,
            body__0__media=MediaFactory(type='video'),
            body__1__media=MediaFactory(type='audio'),
        )

    def test_media_block_translation_of_english_language(self):
        response = self.client.get(self.en_article.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"If you cannot view the above video, you can instead <a href=\"{self.en_article.body[0].value.url}\" download>download it</a>", count=1)
        self.assertContains(response, f"If you cannot listen to the above audio, you can instead <a href=\"{self.en_article.body[1].value.url}\" download>download it</a>", count=1)

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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"উপরের ভিডিও দেখা না গেলে <a href=\"{self.en_article.body[0].value.url}\" download> এর পরিবর্তে এটা </a> ডাউনলোড করুন", count=1)
        self.assertContains(response, f"উপরের অডিও শুনতে না পেলে <a href=\"{self.en_article.body[1].value.url}\" download> এর পরিবর্তে এটা </a> ডাউনলোড করুন", count=1)


class ImageResizeTest(TestCase):
    def setUp(self):
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.site_settings = SiteSettingsFactory(site=self.site)
        self.section = SectionFactory(parent=self.site_settings.site.root_page)
        self.article = ArticleFactory(parent=self.section)

    def test_default_image_within_preset(self):
        response = self.client.get(self.article.url)
        parsed_response = parse_html(response.content)
        rendered_image = parsed_response.find("img", {"class": "article__lead-img-featured"})
        image_rendition = self.article.lead_image.get_rendition('width-360')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)


    def test_half_default_image_within_preset(self):
        response = self.client.get(self.section.url)
        parsed_response = parse_html(response.content)
        rendered_image = parsed_response.find("div", {"class": "article-card"}).find("img")
        image_rendition = self.article.lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    @override_settings(IMAGE_SIZE_PRESET=750)
    def test_custom_image_within_preset(self):
        response = self.client.get(self.article.url)
        parsed_response = parse_html(response.content)
        rendered_image = parsed_response.find("img", {"class": "article__lead-img-featured"})
        image_rendition = self.article.lead_image.get_rendition('width-750')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    @override_settings(IMAGE_SIZE_PRESET=750)
    def test_half_custom_image_within_preset(self):
        response = self.client.get(self.section.url)
        parsed_response = parse_html(response.content)
        rendered_image = parsed_response.find("div", {"class": "article-card"}).find("img")
        image_rendition = self.article.lead_image.get_rendition('width-375')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'lxml')

from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from wagtail.core.models import Site

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SiteSettingsFactory
from wagtail_factories import SiteFactory
from home.models import SiteSettings


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


class ImageResizeTest(TestCase):
    def setUp(self):
        Site.objects.all().delete()
        SiteSettings.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.site_settings = SiteSettingsFactory(site=self.site)
        self.section = SectionFactory(parent=self.site_settings.site.root_page)
        self.article = ArticleFactory(parent=self.section)

    def test_default_image_maximum_width_360(self):
        response = self.client.get(self.article.url)
        soup = BeautifulSoup(response.content)
        rendered_image = soup.find("img", {"class": "article__lead-img-featured"})
        image_rendition = self.article.lead_image.get_rendition('width-360')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    def test_default_image_half_maximum_width_180(self):
        response = self.client.get(self.section.url)
        soup = BeautifulSoup(response.content)
        rendered_image = soup.find("div", {"class": "article-card"}).find("img")
        image_rendition = self.article.lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)


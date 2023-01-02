import factory
from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from wagtail.core.models import Site

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SectionIndexFactory, PageLinkPageFactory
from wagtail_factories import SiteFactory, ImageFactory


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


class PageLinkPageTest(TestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = self.site.root_page
        self.section_index_page = SectionIndexFactory(parent=self.home_page)
        self.section = SectionFactory(parent=self.section_index_page)
        self.section2 = SectionFactory(parent=self.section_index_page)
        self.article = ArticleFactory(parent=self.home_page)

    def test_page_link_page_article_listing(self):
        page_link_page = PageLinkPageFactory(parent=self.section, page=self.article)
        response = self.client.get(self.section.url)
        parsed_response = BeautifulSoup(response.content)
        rendered_title = parsed_response.find("p", {"class": "article-title"}).text
        rendered_image = parsed_response.find("div", {"class": "img-holder"}).find("img")
        image_rendition = self.article.lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_title, page_link_page.get_page().title)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    def test_page_link_page_override_article_listing(self):
        page_link_page = PageLinkPageFactory(
            parent=self.section,
            page=self.article,
            override_title='new title',
            override_lead_image=ImageFactory()
        )

        response = self.client.get(self.section.url)
        parsed_response = BeautifulSoup(response.content)
        rendered_title = parsed_response.find("p", {"class": "article-title"}).text
        rendered_image = parsed_response.find("div", {"class": "article-card"}).find("img")
        image_rendition = page_link_page.specific.override_lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_title, 'new title')
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    def test_page_link_page_section_listing(self):
        page_link_page = PageLinkPageFactory(parent=self.section, page=self.section2)
        response = self.client.get(self.section.url)
        parsed_response = BeautifulSoup(response.content)
        rendered_title = parsed_response.find("p", {"class": "article-title"}).text
        rendered_image = parsed_response.find("div", {"class": "section-card"}).find("img")
        image_rendition = self.section2.lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_title, page_link_page.get_page().title)
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)

    def test_page_link_page_override_section_listing(self):
        page_link_page = PageLinkPageFactory(
            parent=self.section,
            page=self.section2,
            override_title='new title',
            override_lead_image=ImageFactory()
        )

        response = self.client.get(self.section.url)
        parsed_response = BeautifulSoup(response.content)
        rendered_title = parsed_response.find("p", {"class": "article-title"}).text
        rendered_image = parsed_response.find("div", {"class": "section-card"}).find("img")
        image_rendition = page_link_page.specific.override_lead_image.get_rendition('width-180')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rendered_title, 'new title')
        self.assertEqual(rendered_image.get('alt'), image_rendition.alt)
        self.assertEqual(int(rendered_image.get('width')), image_rendition.width)
        self.assertEqual(int(rendered_image.get('height')), image_rendition.height)
        self.assertEqual(rendered_image.get('src'), image_rendition.url)
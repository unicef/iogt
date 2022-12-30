from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from wagtail.core.models import Site
from wagtail.core.rich_text import RichText

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory
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


class HomePageFeaturedItemBlockTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.home_page = self.site.root_page.specific

    def test_home_page_featured_item_heading_block(self):
        self.home_page.home_featured_content.append(('heading', 'Test Heading'))
        self.home_page.save()

        response = self.client.get(self.home_page.url)
        parsed_response = BeautifulSoup(response.content)
        heading_block_text = parsed_response.find("div", {"class": "block-heading"}).text.strip()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(heading_block_text, 'Test Heading')

    def test_home_page_featured_item_paragraph_block(self):
        self.home_page.home_featured_content.append(('paragraph', RichText('<p>Test Paragraph</p>')))
        self.home_page.save()

        response = self.client.get(self.home_page.url)
        parsed_response = BeautifulSoup(response.content)
        paragraph_block_text = parsed_response.find("div", {"class": "block-paragraph"}).text.strip()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(paragraph_block_text, 'Test Paragraph')

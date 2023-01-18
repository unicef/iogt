from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from django.urls import reverse
from wagtail.core.models import Site, Page

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SectionIndexFactory
from wagtail_factories import SiteFactory

from iogt_users.factories import AdminUserFactory


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


class PageViewTest(TestCase):
    def setUp(self):
        root_page = Page.objects.filter(depth=1).first()
        self.home_page = HomePageFactory(parent=root_page)
        SiteFactory(hostname='testserver', port=80, root_page=self.home_page)
        user = AdminUserFactory()

        self.section_index_page = SectionIndexFactory(parent=self.home_page)
        self.client.force_login(user)

    def test_view_live_button_on_parent_page_listing(self):
        response = self.client.get(reverse('wagtailadmin_explore', args=[self.home_page.pk]))
        parsed_response = BeautifulSoup(response.content)
        view_live_button = parsed_response.find("tbody").find("ul", {"class": "actions"}).find("a", {"title": "View live"})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(view_live_button)

    def test_view_live_buttons_on_edit_page(self):
        response = self.client.get(reverse('wagtailadmin_pages:edit', args=[self.section_index_page.pk]))
        parsed_response = BeautifulSoup(response.content)
        header_live_button = parsed_response.find("header").find("a", {"title": "Visit the live page"})
        footer_preview_button = parsed_response.find("footer").find("li", {"class": "preview"}).find("button")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(header_live_button)
        self.assertIsNone(footer_preview_button)




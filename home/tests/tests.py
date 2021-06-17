from django.test import TestCase, Client
from django.http import HttpRequest
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import PageViewRestriction

from home.factories import ArticleFactory, SectionFactory
from home.models import HomePage
from iogt_users.factories import UserFactory
from home.wagtail_hooks import limit_page_chooser


class LimitPageChooserHookTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.home_page = HomePage.objects.first()
        self.article01 = ArticleFactory.build(owner=self.user)
        self.section01 = SectionFactory.build(owner=self.user)
        self.home_page.add_child(instance=self.article01)
        self.home_page.add_child(instance=self.section01)
        self.section02 = SectionFactory.build(owner=self.user)
        self.article02 = ArticleFactory.build(owner=self.user)
        self.section01.add_child(instance=self.section02)
        self.section01.add_child(instance=self.article02)

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

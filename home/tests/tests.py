from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from rest_framework import status
from wagtail.core.models import Site

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, FlatMenuFactory, IogtFlatMenuItemFactory
from wagtail_factories import SiteFactory

from questionnaires.factories import QuizFactory, SurveyFactory, PollFactory
from home.models import IogtFlatMenuItem

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


class FlatMenuTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.home_page = self.site.root_page
        self.flat_menu = FlatMenuFactory(site=self.site, handle='en_menu_live', title='Flat Menu')
        self.article = ArticleFactory(parent=self.home_page, title='test article')
        self.survey = SurveyFactory(parent=self.home_page, title='test survey')
        self.quiz = QuizFactory(parent=self.home_page, title='test quiz')
        self.poll = PollFactory(parent=self.home_page, title='test poll')

    def test_flat_menu_item_display(self):
        IogtFlatMenuItemFactory(menu=self.flat_menu, link_page=self.article, link_text=self.article.title)
        IogtFlatMenuItemFactory(menu=self.flat_menu, link_page=self.survey, link_text=self.survey.title)
        IogtFlatMenuItemFactory(menu=self.flat_menu, link_page=self.quiz, link_text=self.quiz.title)
        IogtFlatMenuItemFactory(menu=self.flat_menu, link_page=self.poll, link_text=self.poll.title)

        response = self.client.get(self.home_page.url)
        parsed_response = BeautifulSoup(response.content)
        flat_menu_items = parsed_response.findAll('a', {'class': 'btn-primary menu-item'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(flat_menu_items[0].text.strip(), 'test article')
        self.assertEqual(flat_menu_items[0]['href'], self.article.url)
        self.assertEqual(flat_menu_items[1].text.strip(), 'test survey')
        self.assertEqual(flat_menu_items[1]['href'], self.survey.url)
        self.assertEqual(flat_menu_items[2].text.strip(), 'test quiz')
        self.assertEqual(flat_menu_items[2]['href'], self.quiz.url)
        self.assertEqual(flat_menu_items[3].text.strip(), 'test poll')
        self.assertEqual(flat_menu_items[3]['href'], self.poll.url)
